import sys
import subprocess

subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q', '--disable-pip-version-check', '--user', 'netifaces','python-whois','python-nmap','netaddr'])

#flag = sys.argv[1]
#print(flag)
import platform
import socket
import sys
#import whois
import netifaces as ni
import json
from netaddr import IPAddress
import ipaddress
#import nmap 

iface = ni.gateways()['default'][ni.AF_INET][1]
ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
os = platform.system()
if os == 'Linux':
    process = subprocess.Popen(['sudo','apt','install','nmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
elif os == 'Darwin':
    process = subprocess.Popen(['sudo','brew','install','nmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
else:
    print("Not compatible with Windows ")
    exit()

import nmap

range = (ip + "/" + str(IPAddress(ni.ifaddresses(iface)[ni.AF_INET][0]['netmask']).netmask_bits()))
#range2 = ipaddress.IPv4Network(range,False)
nm = nmap.PortScanner()
data = nm.scan(hosts=range,arguments='-sn')['scan']
#print(data)
final = {}
oops=""
for ip in data.keys():
    ans={'IP':"",'MAC':"",'Hostname':"",'OS':""}
    try:
        
        ans['IP'] = ip
        print(data[ip])
        ans['MAC'] = data[ip]['addresses']['mac']
        ans['Hostname'] = data[ip]['hostnames'][0]['name']
        oops = nm.scan(hosts=ip, arguments="-O -p T:22,443,80,U:53")['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
        ans['OS'] = oops #print(oops)
    except:
        ans['OS'] = ''
    
    final[ip] = ans
    #print("Port not found for IP : "+ip)

print(json.dumps(final))
