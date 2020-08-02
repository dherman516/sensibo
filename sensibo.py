import requests
import json
import math
from meteocalc import Temp, dew_point, heat_index, wind_chill, feels_like

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
    parser.add_argument('apikey2', type = str, help='Request an API Key from http://api.openweathermap.org/')
    parser.add_argument('deviceName', type = str, help='Your sensibo device name from home.sensibo.com')
    parser.add_argument('cityLat', type = str, help='Lattitude of the city you live in')
    parser.add_argument('cityLon', type = str, help='Longitude of the city you live in')
    parser.add_argument('offset', type = int, help='number of degrees C offset from ambient to use', default=0)
    parser.add_argument('ReactHot', type = int, help='Temp in C offset for trigger AC turn On', default=27)
    parser.add_argument('ReactOff', type = int, help='Temp in C offset for trigger Climate Off ', default=22)
    parser.add_argument('ReactCold', type = int, help='Temp in C offset for trigger Heat turn On', default=18)

    args = parser.parse_args()
    offset=args.offset
    cityLat=args.cityLat
    cityLon=args.cityLon
    ReactHot=args.ReactHot
    ReactOff=args.ReactOff
    ReactCold=args.ReactCold

    f = open("/tmp/sensibo.log","a+")
    f.write(timestamp + "\n")
   
    g = open("/tmp/sensibo.data.log","a+")
    g.write(timestamp + ",")
   
    

    client = SensiboClientAPI(args.apikey)
    weathAPIkey = args.apikey2
    devices = client.devices()
    print "-" * 10, "devices", "-" * 10
    print devices
    f.write ("--------Devices---------\n")
    f.write ("Devices {} \n".format(devices))


   
    uid = devices[args.deviceName]
    ac_state = client.pod_ac_state(uid)
    print "-" * 10, "AC State of %s" % args.deviceName, "_" * 10
	

    #targettemp = ac_state['result'][0]['device']['acState']['nativeTargetTemperature']
    targettemp = ac_state['result'][0]['device']['acState']['targetTemperature']
    sensibotemp= ac_state['result'][0]['device']['measurements']['temperature']
    sensibohumidity= ac_state['result'][0]['device']['measurements']['humidity']
    sensibomode = ac_state['result'][0]['acState']['mode']
    fanlevel = ac_state['result'][0]['acState']['fanLevel']
    power = ac_state['result'][0]['acState']['on']	
	
#    print ac_state
#    print(json.dumps(ac_state, indent=4, sort_keys=True))
#    client.pod_change_ac_state(uid, ac_state, "on", not ac_state['on'])
#    Sensibo moved nativeTargetTemperature out of the acstate structure into device/acstate
#    print ac_state['result'][0]['device']['acState']['nativeTargetTemperature']

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat=' + cityLat + '&lon=' + cityLon + '&units=metric&exclude=hourly,daily&appid=' + weathAPIkey
    response = requests.get(url)
    response.raise_for_status()
    weather = response.json()
    outsideTemp = weather['current']['temp']
    fahrenheit = (outsideTemp * 9/5) + 32
 
    # create input temperature in different units
    t = Temp(sensibotemp, 'c')  # c - celsius, f - fahrenheit, k - kelvin
    # calculate Heat Index
    tRealFeel = heat_index(temperature=t, humidity=sensibohumidity)
    RealFeel = tRealFeel.c


#    r = requests.get('http://wttr.in/' + cityName + '?format=%t')
#    s = r.text[1:-2]
#    outsideTemp = float(s)
#    fahrenheit = (outsideTemp * 9/5) + 32


    g.write ("{},{},{},{},{},{:.2f},{:.2f}\n".format(power,sensibotemp,sensibomode,fanlevel,targettemp,outsideTemp,RealFeel,sensibohumidity))
    f.write ("--------Temps---------\n")
    f.write ("Target Temp: {}\n".format(targettemp))
    f.write ("Sensibo Power On: {} Temp: {} Humidity: {:.2f} % RealFeel: {:.2f} State: {}  Fan: {}\n".format(power,sensibotemp,sensibohumidity,RealFeel,sensibomode,fanlevel))
    f.write ("Outside Temp: {}C /{}F\n".format(outsideTemp,fahrenheit))
	
    print "--------Temps---------\n"
    print "Target Temp: {}\n".format(targettemp)
    print "Sensibo Power On: {} Temp: {} Humidity: {:.2f} % RealFeel: {:.2f} State: {}  Fan: {}\n".format(power,sensibotemp,sensibohumidity,RealFeel,sensibomode,fanlevel)
    print "Outside Temp: {}C /{}F\n".format(outsideTemp,fahrenheit)
	
	
    f.write ("--------Analysis---------\n")
    
    if (False == power) :    #climate react Onlogic
      if  (outsideTemp > targettemp ) and (RealFeel > ReactHot ) and ("cool" == sensibomode):
        print "Climate react [AC ON] Outside air {} Warmer than target {} temp".format(outsideTemp,targettemp)
	print "Climate react [AC ON] Inside air {} Warmer than ClimateReact {} temp".format(RealFeel,ReactHot)
	f.write ("Climate react [AC ON] Outside air {} Warmer than target {} temp \n".format(outsideTemp,targettemp))
	f.write ("Climate react [AC ON] Inside air {} Warmer than ClimateReact {} temp \n".format(RealFeel,ReactHot))
        client.pod_change_ac_state(uid, ac_state, "on", True)
      if  (outsideTemp < targettemp ) and (sensibotemp < ReactCold ) and ("heat" == sensibomode):
        print "Climate react [Heat ON] Outside air {} Colder than target {} temp".format(outsideTemp,targettemp)
	print "Climate react [Heat ON] Inside air {} Colder than ClimateReact {} temp".format(RealFeel,ReactCold)
	f.write ("Climate react [Heat ON] Outside air {} Colder than target {} temp \n".format(outsideTemp,targettemp))
	f.write ("Climate react [Heat ON] Inside air {} Colder than ClimateReact {} temp\n".format(RealFeel,ReactCold))
        client.pod_change_ac_state(uid, ac_state, "on", True)
    else:  #Power On Climate React Off
      if  (sensibotemp < ReactOff ) and ("cool" == sensibomode):
        print "Climate react [AC ON] Inside air {} Colder than target {} temp".format(RealFeel,ReactOff)
	f.write ("Climate react [AC ON] Inside air {} Colder than target {} temp {}\n".format(RealFeel,ReactOff))
        client.pod_change_ac_state(uid, ac_state, "on", False)
      if  (sensibotemp > ReactOff ) and ("heat" == sensibomode):
        print "Climate react [Heat ON] Inside air {} Warmer than target {} temp".format(sensibotemp,ReactOff)
	f.write ("Climate react [Heat  ON] Inside air {} Warmer than target {} temp {}\n".format(sensibotemp,ReactOff))
        client.pod_change_ac_state(uid, ac_state, "on", False)	
	 
    #regular logic for fan control
    if ("cool" == sensibomode) :
      if (outsideTemp + offset < targettemp  ):
        print "[AC Off] Outside air {} plus offset {} lower than target {} temp".format(outsideTemp,offset,targettemp)
        f.write ("[AC Off] Outside air {} plus offset {} lower than target {} temp".format(outsideTemp,offset,targettemp))
        client.pod_change_ac_state(uid, ac_state, "on", False)
      if ("high" <> fanlevel) :
           if (RealFeel > targettemp) :
             print "Fan is not high, Interior temp {:.2f} too high raising fan".format(RealFeel)
             f.write ("Fan is not high, Interior temp {:.2f} too high raising fan\n".format(RealFeel))
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")             
    else:  #Heating Mode
      if (outsideTemp > targettemp) :
        print "[Heat Off] Outside air {} higher than target {} temp".format(outsideTemp,targettemp)
        f.write("[Heat Off] Outside air {} higher than target {} temp\n".format(outsideTemp,targettemp))
        client.pod_change_ac_state(uid, ac_state, "on", False)        

      if ("high" <> fanlevel) :
           if (RealFeel < targettemp ) :
             print "Fan is not high, Interior temp {:.2f} too low raising fan".format(RealFeel)
             f.write ("Fan is not high, Interior temp {:.2f} too low raising fan\n".format(RealFeel))
             client.pod_change_ac_state(uid, ac_state, "fanLevel", "high")             
    if (outsideTemp < RealFeel) :
      print "Inside {:.2f} hotter than Outside {}".format(RealFeel,outsideTemp)
    else:
      print "Outside {} hotter than Inside {:.2f}".format(outsideTemp,RealFeel)
    if (RealFeel == targettemp) :
        print "Target Temp {} reached. Reducing Fan".format(targettemp)
        client.pod_change_ac_state(uid, ac_state, "fanLevel", "low")
        f.write ("Target Temp reached reducing fan\n")
  

