import requests
import json

_SERVER = 'https://home.sensibo.com/api/v2'

class SensiboClientAPI(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _get(self, path, ** params):
        params['apiKey'] = self._api_key
        response = requests.get(_SERVER + path, params = params)
        response.raise_for_status()
        return response.json()

    def _jget(self, path, ** params):
        params['apiKey'] = self._api_key
        response = requests.get(_SERVER + path, params = params)
        return response

    def _patch(self, path, data, ** params):
        params['apiKey'] = self._api_key
        response = requests.patch(_SERVER + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def devices(self):
        result = self._get("/users/me/pods", fields="id,room")
        return {x['room']['name']: x['id'] for x in result['result']}

    def pod_measurement(self, podUid):
        result = self._get("/pods/%s/measurements" % podUid)
        return result['result']

    def pod_timer(self, podUid):
        result = self._get("/pods/%s/timer" % podUid)
        return result['result']

    def pod_ac_state(self, podUid):
        response = self._jget("/pods/%s/acStates" % podUid, limit = 1, fields="acState,device")
        response.raise_for_status()
        return response.json()


    def pod_change_ac_state(self, podUid, currentAcState, propertyToChange, newValue):
        self._patch("/pods/%s/acStates/%s" % (podUid, propertyToChange),
                json.dumps({'currentAcState': currentAcState, 'newValue': newValue}))

if __name__ == "__main__":
    import argparse
    import time
    timestamp  = time.asctime( time.localtime(time.time()) )
   
   
    parser = argparse.ArgumentParser(description='Sensibo client example parser')
    parser.add_argument('apikey', type = str)
    parser.add_argument('deviceName', type = str)
    args = parser.parse_args()

    f = open("/tmp/sensibo.log","a+")
    f.write(timestamp + "\n")
   
    client = SensiboClientAPI(args.apikey)
    devices = client.devices()
    print "-" * 10, "devices", "-" * 10
    print devices
    f.write ("--------Devices---------\n")
    f.write ("Devices {} \n".format(devices))

   
    uid = devices[args.deviceName]
    ac_state = client.pod_ac_state(uid)
    print "-" * 10, "AC State of %s" % args.deviceName, "_" * 10
#    print ac_state
#    print(json.dumps(ac_state, indent=4, sort_keys=True))
#    client.pod_change_ac_state(uid, ac_state, "on", not ac_state['on'])
    print ac_state['result'][0]['device']['acState']['nativeTargetTemperature']
    r = requests.get('http://wttr.in/Modiin?format=%t')
    s = r.text[1:-3]
    celsius = float(s)
    fahrenheit = (celsius * 9/5) + 32
#    print  ac_state['result'][0]['device']['measurements']

    targettemp = ac_state['result'][0]['device']['acState']['nativeTargetTemperature']
    sensibotemp= ac_state['result'][0]['device']['measurements']['temperature']
    sensibomode = ac_state['result'][0]['acState']['mode']
    fanlevel = ac_state['result'][0]['acState']['fanLevel']
    power = ac_state['result'][0]['acState']['on']
    f.write ("--------Temps---------\n")
    f.write ("Target Temp: {}\n".format(targettemp))
    f.write ("Sensibo Power On: {} Temp: {} State: {}  Fan: {}\n".format(power,sensibotemp,sensibomode,fanlevel))
    f.write ("Outside Temp: {}C /{}F\n".format(celsius,fahrenheit))
    f.write ("--------Analysis---------\n")
    
    #climate react logic
    if (False == power) and (celsius >= targettemp ) and (sensibotemp > targettemp +5 ) and ("cool" == sensibomode):
        print "Clmate react Cooling: Outside air {} lower than target {} temp".format(celsius,targettemp)
        f.write ("Turning On AC\n")
        client.pod_change_ac_state(uid, ac_state, "on", True)
	
	#regular logic for fan control
    if ("cool" == sensibomode) :
      if (celsius + 5 < targettemp  ):
        print "Cooling: Outside air {} lower than target {} temp".format(celsius,targettemp)
        f.write ("Turning Off AC\n")
        client.pod_change_ac_state(uid, ac_state, "on", False)
      else:
        print "Cooling: Outside air {} higher than target {} temp".format(celsius,targettemp)
        f.write ("Keep Cooling\n")
      if ("high" <> fanlevel) :
           if (sensibotemp > targettemp + 1) :
             print "Fan is not high, Interior temp {} too high raising fan".format(sensibotemp)
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")
             f.write ("Kicking up fan\n")
    else:  #Heating Mode
      if (celsius > targettemp) :
        print "Heating: Outside air {} higher than target {} temp".format(celsius,targettemp)
        client.pod_change_ac_state(uid, ac_state, "on", False)
        f.write ("Turning Off Heat\n")
      else:
        print "Heating: Outside air {} lower than target {} temp".format(celsius,targettemp)
        f.write ("Keep Heating\n")
      if ("high" <> fanlevel) :
           if (sensibotemp < targettemp - 1) :
             print "Fan is not high, Interior temp {} too low raising fan".format(sensibotemp)
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")
             f.write ("Kicking up fan\n")
    if (celsius < sensibotemp) :
      print "Inside {} hotter than Outside {}".format(sensibotemp,celsius)
    else:
      print "Outside {} hotter than Inside {}".format(celsius,sensibotemp)
    if (sensibotemp == targettemp) :
        print "Target Temp {} reached. Reducing Fan".format(targettemp)
        client.pod_change_ac_state(uid, ac_state, "fanLevel", "low")
        f.write ("Target Temp reached reducing fan\n")
  

