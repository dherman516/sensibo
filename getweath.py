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
