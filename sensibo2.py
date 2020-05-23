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
   
   
    parser = argparse.ArgumentParser(description='Sensibo client parser')
    parser.add_argument('apikey', type = str, help='Request an API Key from home.sensibo.com')
    parser.add_argument('deviceName', type = str, help='Your sensibo device name from home.sensibo.com')
    parser.add_argument('cityName', type = str, help='Name of the city you live in', default='Modiin')	
    parser.add_argument('offset', type = int, help='number of degrees C offset from ambient to use', default=0)

    args = parser.parse_args()
    offset=args.offset
    cityName=args.cityName

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
#    Sensibo moved nativeTargetTemperature out of the acstate structure into device/acstate
#    print ac_state['result'][0]['device']['acState']['nativeTargetTemperature']
    r = requests.get('http://wttr.in/' + cityName + '?format=%t')
    s = r.text[1:-3]
    outsideTemp = float(s)
    fahrenheit = (outsideTemp * 9/5) + 32

    targettemp = ac_state['result'][0]['device']['acState']['nativeTargetTemperature']
    sensibotemp= ac_state['result'][0]['device']['measurements']['temperature']
    sensibomode = ac_state['result'][0]['acState']['mode']
    fanlevel = ac_state['result'][0]['acState']['fanLevel']
    power = ac_state['result'][0]['acState']['on']
    f.write ("--------Temps---------\n")
    f.write ("Target Temp: {}\n".format(targettemp))
    f.write ("Sensibo Power On: {} Temp: {} State: {}  Fan: {}\n".format(power,sensibotemp,sensibomode,fanlevel))
    f.write ("Outside Temp: {}C /{}F\n".format(outsideTemp,fahrenheit))
    f.write ("--------Analysis---------\n")
    
    #climate react logic
    if (False == power) and (outsideTemp > targettemp ) and (sensibotemp > targettemp + offset ) and ("cool" == sensibomode):
        print "Climate react [AC ON] Outside air {} Warmer than target {} temp plus offset {}".format(outsideTemp,targettemp,offset)
	f.write ("Climate react [AC ON] Outside air {} Warmer than target {} temp plus offset {}\n".format(outsideTemp,targettemp,offset))
        client.pod_change_ac_state(uid, ac_state, "on", True)
    if (False == power) and (outsideTemp < targettemp ) and (sensibotemp < targettemp - offset ) and ("heat" == sensibomode):
        print "Climate react [Heat ON] Outside air {} Cooler than target {} temp less offset {}".format(outsideTemp,targettemp,offset)
	f.write ("Climate react [Heat ON] Outside air {} Coller than target {} temp less offset {}\n".format(outsideTemp,targettemp,offset))
        client.pod_change_ac_state(uid, ac_state, "on", True)
	 
    #regular logic for fan control
    if ("cool" == sensibomode) :
      if (outsideTemp + offset < targettemp  ):
        print "[AC Off] Outside air {} plus offset {} lower than target {} temp".format(outsideTemp,offset,targettemp)
        f.write ("[AC Off] Outside air {} plus offset {} lower than target {} temp".format(outsideTemp,offset,targettemp))
        client.pod_change_ac_state(uid, ac_state, "on", False)
      if ("high" <> fanlevel) :
           if (sensibotemp > targettemp) :
             print "Fan is not high, Interior temp {} too high raising fan".format(sensibotemp)
             f.write ("Fan is not high, Interior temp {} too high raising fan\n".format(sensibotemp))
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")             
    else:  #Heating Mode
      if (outsideTemp > targettemp) :
        print "[Heat Off] Outside air {} higher than target {} temp".format(outsideTemp,targettemp)
        f.write("[Heat Off] Outside air {} higher than target {} temp\n".format(outsideTemp,targettemp))
        client.pod_change_ac_state(uid, ac_state, "on", False)        

      if ("high" <> fanlevel) :
           if (sensibotemp < targettemp ) :
             print "Fan is not high, Interior temp {} too low raising fan".format(sensibotemp)
             f.write ("Fan is not high, Interior temp {} too low raising fan\n".format(sensibotemp))
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")             
    if (outsideTemp < sensibotemp) :
      print "Inside {} hotter than Outside {}".format(sensibotemp,outsideTemp)
    else:
      print "Outside {} hotter than Inside {}".format(outsideTemp,sensibotemp)
    if (sensibotemp == targettemp) :
        print "Target Temp {} reached. Reducing Fan".format(targettemp)
        client.pod_change_ac_state(uid, ac_state, "fanLevel", "low")
        f.write ("Target Temp reached reducing fan\n")
  

