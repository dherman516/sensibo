# sensibo-python-sdk
Sensibo Python SDK
https://sensibo.github.io/

Requirements:
requests: http://www.python-requests.org/en/latest/
# sensibo

Logs to /tmp/sensibo.txt

Log looks like:

2020-05-16 18:08:55  
--------Devices---------  
Devices {u'apartment': u'9eYvK8PQ'}  
--------Temps---------  
Target Temp: 23  
Sensibo Power On: True Temp: 24.6 State: cool  Fan: high  
Outside Temp: 34.0C /93.2F  
--------Analysis---------  
Keep Cooling  


turn off implemented for cases where 
    outside temp < desired temp for cooling  
    outside temp > desired temp for Heating  

Added logic if fan is not set to High and interior temp is +1 from target, raise fan to high

If interior temp is equal to target drop fan to low

Sample command line  
Python sensibo.py [api key] [device name] [City Name] [Offset] [React Temp Hot] [React Temp Off] [React Temp Cold]

Get api key from sensibo API page (https://home.sensibo.com/me/api)
get device name from home.sensibo.com, mine is "apartment"  
Sample Output  

---------- devices ----------  
{u'apartment': u'9eYvK8PQ'}  
--------- AC State of apartment __________  
Cooling: Outside air 27.0 higher than target 23 temp  
Outside 27.0 hotter than Inside 25.4  

I added to a cron job and it runs every 15 minutes
