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
    parser = argparse.ArgumentParser(description='Sensibo client example parser')
    parser.add_argument('apikey', type = str)
    parser.add_argument('deviceName', type = str)
    args = parser.parse_args()

    client = SensiboClientAPI(args.apikey)
    devices = client.devices()
    print "-" * 10, "devices", "-" * 10
    print devices

    uid = devices[args.deviceName]
    ac_state = client.pod_ac_state(uid)
    print "-" * 10, "AC State of %s" % args.deviceName, "_" * 10
#    print ac_state
#    print(json.dumps(ac_state, indent=4, sort_keys=True))
#    client.pod_change_ac_state(uid, ac_state, "on", not ac_state['on'])
#    print ac_state['result'][0]['acState']['nativeTargetTemperature']
    r = requests.get('http://wttr.in/Modiin?format=%t')
    s = r.text[1:-3]
    celsius = float(s)
    fahrenheit = (celsius * 9/5) + 32
#    print  ac_state['result'][0]['device']['measurements']

    targettemp = ac_state['result'][0]['acState']['nativeTargetTemperature']
    sensibotemp= ac_state['result'][0]['device']['measurements']['temperature']
    sensibomode = ac_state['result'][0]['acState']['mode'] 
    if ("cool" == sensibomode) :
      if (celsius <= targettemp ): 
        print "Cooling: Outside air {} lower than target {} temp".format(celsius,targettemp)
        client.pod_change_ac_state(uid, ac_state, "on", False)
      else:
	print "Cooling: Outside air {} higher than target {} temp".format(celsius,targettemp)
    else:
      if (celsius >= targettemp) :
        print "Heating: Outside air {} higher than target {} temp".format(celsius,targettemp)
        client.pod_change_ac_state(uid, ac_state, "on", False)
      else:
        print "Heating: Outside air {} lower than target {} temp".format(celsius,targettemp)
    if (celsius < sensibotemp) :
      print "Inside {} hotter than Outside {}".format(sensibotemp,celsius)
    else:
      print "Outside {} hotter than Inside {}".format(celsius,sensibotemp)
    if (sensibotemp == targettemp) :
	print "Target Temp {} reached. Reducing Fan".format(targettemp)
	client.pod_change_ac_state(uid, ac_state, "fanLevel", "low")
    if ("high" <> ac_state['result'][0]['acState']['fanLevel']) :
      if (sensibotemp > targettemp + 1) :
        print "Fan is not high, Interior temp {} too high raising fan".format(sensibotemp)
        client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")

