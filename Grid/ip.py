import sys
import subprocess

subprocess.check_call([sys.executable, '-m', 'pip', 'install','-q', '--disable-pip-version-check', '--user', 'netifaces','python-nmap','netaddr'])

import platform
import socket
import sys
import netifaces as ni
import json
from netaddr import IPAddress
import ipaddress

iface = ni.gateways()['default'][ni.AF_INET][1]
ipo = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
os = platform.system()

import nmap

range = (ipo + "/" + str(IPAddress(ni.ifaddresses(iface)[ni.AF_INET][0]['netmask']).netmask_bits()))
nm = nmap.PortScanner()
data = nm.scan(hosts=range,arguments='-sn')['scan']

final = {}
host_OS=""
for ip in data.keys():
	scan_data={'IP':"",'MAC':"",'Hostname':"",'OS':"",'Status':"",'ADDomain':"",'Workgroup':""}
	if ip == ipo:
		scan_data['IP'] = ipo
		scan_data['MAC'] = ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']
		scan_data['Hostname'] =  socket.gethostname()
		scan_data['Status'] = "up"
		scan_data['OS'] = platform.system()
	else:
		try:
			scan_data['IP'] = ip
			scan_data['Hostname'] = data[ip]['hostnames'][0]['name']
			scan_data['Status'] = data[ip]['status']['state']
			try:
				scan_data['MAC'] = data[ip]['addresses']['mac']
				host_OS = nm.scan(hosts=ip, arguments="-O -p T:22,443,80,U:53")['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
				scan_data['OS'] = host_OS
			except:
				host_OS = nm.scan(hosts=ip, arguments="-O -p T:22,443,80,U:53")['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
				scan_data['OS'] = host_OS			
		except:
			scan_data['OS'] = ''
	scan_data['Status'] = "up"
	
	
	final[ip] = scan_data

print(json.dumps(final))


