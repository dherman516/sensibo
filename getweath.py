#Sample code to grab local weather (temp) and print it out

import requests,re
r = requests.get('http://wttr.in/Modiin?format=%t')
print r.text
temp = re.findall(r'\d+', r.text)
res = list(map(int, temp))
# print result
print("The numbers list is : " + str(res))

s = r.text[1:-2] #Change due to wttr change in output format
print s
celsius = float(s)
fahrenheit = (celsius * 9/5) + 32
print('%.2f Celsius is: %0.2f Fahrenheit' %(celsius, fahrenheit))

# I use a Python script to pull current weather conditions from the NOAA web service API. The NOAA web
# service does not return a windchill value for all locations, but given temperature, relative humidity,
# and wind speed you can calculate a “feels like” temperature as follows.

# This code assumes units of Fahrenheit, MPH, and Relative Humidity by percentage.  In this example, a
# temperature of 35F, wind speed of 10mph, and relative humidity of 72% yields a "feels like" value of 27.4F
 
import math
 
vTemperature = fahrenheit
vRelativeHumidity = float(72)

 
# Replace it with the Heat Index, if necessary
if vFeelsLike == vTemperature and vTemperature >= 80:
  vFeelsLike = 0.5 * (vTemperature + 61.0 + ((vTemperature-68.0)*1.2) + (vRelativeHumidity*0.094))
 
  if vFeelsLike >= 80:
    vFeelsLike = -42.379 + 2.04901523*vTemperature + 10.14333127*vRelativeHumidity - .22475541*vTemperature*vRelativeHumidity - .00683783*vTemperature*vTemperature - .05481717*vRelativeHumidity*vRelativeHumidity + .00122874*vTemperature*vTemperature*vRelativeHumidity + .00085282*vTemperature*vRelativeHumidity*vRelativeHumidity - .00000199*vTemperature*vTemperature*vRelativeHumidity*vRelativeHumidity
    if vRelativeHumidity < 13 and vTemperature >= 80 and vTemperature <= 112:
      vFeelsLike = vFeelsLike - ((13-vRelativeHumidity)/4)*math.sqrt((17-math.fabs(vTemperature-95.))/17)
      if vRelativeHumidity > 85 and vTemperature >= 80 and vTemperature <= 87:
        vFeelsLike = vFeelsLike + ((vRelativeHumidity-85)/10) * ((87-vTemperature)/5)				
 
print "Feels like: " + '%0.1f' % (vFeelsLike) + "F"
# Feels like: 27.4F
