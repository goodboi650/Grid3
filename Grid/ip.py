import sys
import subprocess

subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q', '--disable-pip-version-check', '--user', 'netifaces','python-nmap','netaddr'])

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
ipo = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
os = platform.system()
'''if os == 'Linux':
	process = subprocess.Popen(['sudo','apt','install','nmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
elif os == 'Darwin':
	process = subprocess.Popen(['sudo','brew','install','nmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
else:
	print("Not compatible with Windows ")
	exit()

subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q', '--disable-pip-version-check', '--user','python-nmap'])
'''

import nmap

range = (ipo + "/" + str(IPAddress(ni.ifaddresses(iface)[ni.AF_INET][0]['netmask']).netmask_bits()))
#range2 = ipaddress.IPv4Network(range,False)
nm = nmap.PortScanner()
data = nm.scan(hosts=range,arguments='-sn')['scan']
#data2 = nm.scan(hosts=range,arguments='-p 139,445 --script smb-os-discovery.nse,smb-protocols.nse')['scan']
#print(data)


#exit()
final = {}
oops=""
for ip in data.keys():
	ans={'IP':"",'MAC':"",'Hostname':"",'OS':"",'Status':"",'ADDomain':"",'Workgroup':""}
	if ip == ipo:
		ans['IP'] = ipo
		ans['MAC'] = ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']
		ans['Hostname'] =  socket.gethostname()
		ans['Status'] = "up"
		ans['OS'] = platform.system()
	else:
		try:
			ans['IP'] = ip
			#print(data[ip])
			ans['Hostname'] = data[ip]['hostnames'][0]['name']
			ans['Status'] = data[ip]['status']['state']
			try:
				ans['MAC'] = data[ip]['addresses']['mac']
				oops = nm.scan(hosts=ip, arguments="-O -p T:22,443,80,U:53")['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
				ans['OS'] = oops #print(oops)
			except:
				oops = nm.scan(hosts=ip, arguments="-O -p T:22,443,80,U:53")['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
				ans['OS'] = oops #print(oops)			
		except:
			ans['OS'] = ''
	ans['Status'] = "up"
	
	
	final[ip] = ans
	#print("Port not found for IP : "+ip)

print(json.dumps(final))


