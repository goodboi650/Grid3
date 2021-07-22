import sys
import subprocess

# implement pip as a subprocess:
#subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q','netifaces','python-whois'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q', '--disable-pip-version-check', '--user', 'netifaces','python-whois'])


import platform
import socket
import sys
import netifaces as ni
import json

#sys.stdout = open('output.txt', 'w')
host = socket.gethostname()
iface = ni.gateways()['default'][ni.AF_INET][1]
ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
mac = ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']
#ip = socket.gethostbyname(host)
#mac = hex(uuid.getnode())
opsys = platform.system()
dom = ''
output = {}
output['IP'] = ip
output['MAC'] = mac
output['Hostname'] = host
output['OS'] = opsys
output['Domain Info'] = dom
json_out = json.dumps(output)
print(json_out)
#print('IP       :   ', ip)
#print('Hostname :   ', host)
#print('MAC      :   ', mac)
#print('OS       :   ', opsys)
#print()
#print('Domain information :')
#print(dom)


#sys.stdout.close()