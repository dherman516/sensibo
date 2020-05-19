#Sample code to grab local weather (temp) and print it out

import requests
r = requests.get('http://wttr.in/Modiin?format=%t')
print r.text
s = r.text[1:-3]
print s
celsius = float(s)
fahrenheit = (celsius * 9/5) + 32
print('%.2f Celsius is: %0.2f Fahrenheit' %(celsius, fahrenheit))
