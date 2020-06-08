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

    def pod_historical(self, podUid, days):
        result = self._jget("/pods/%s/historicalMeasurements" % podUid, limit = 1, {'days': days})
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
    parser.add_argument('days', type = int, help='Number of days of History to grab')

    args = parser.parse_args()
    days=args.days   
    g = open("/tmp/sensibo.data.log","a+")
    g.write("datetime,power,sensibotemp,sensibomode,fanlevel,targettemp,outsideTemp\n")
    g.write(timestamp + ",")
   
    

    client = SensiboClientAPI(args.apikey)
    devices = client.devices()
    print "-" * 10, "devices", "-" * 10
    print devices

   
    uid = devices[args.deviceName]
    history = client.pod_historical(uid,days)
    print "-" * 10, "AC State of %s" % args.deviceName, "_" * 10
    print history
