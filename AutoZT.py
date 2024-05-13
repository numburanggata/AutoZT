import nmap
import socket
import argparse
import subprocess
import re
import multiprocessing
import time

private_subnets = ['192.168.0.0/16', '172.16.0.0/12', '10.0.0.0/8']
with open('common_ports.txt', 'r') as file:
    # Read the lines of the file and store them as elements in a list
    common_ports = file.readlines()
str_common_ports = [ports.strip() for ports in common_ports]
str_common_ports = ', '.join(str_common_ports)
# print (str_common_ports)

def extract_ip(ip_string):
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    # Use re.findall to find all matches in the input string
    matches = re.findall(ip_pattern, ip_string)

    # Return the first match (if any)
    if matches:
    	return matches[0] 

def traceroute(): #AKAN DIBUAT PARALEL DGN MULTITHREADING
	print("INISIASI TRACEROUTE...")
	result = subprocess.Popen(['traceroute', '-m 3', '-S', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #LINUX
	# result = subprocess.Popen(['tracert','-h','3','-w','1','-d','8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #WINDOWS
	# print(list(result.stdout))
	# match = extract_ip(' '.join(list(result.stdout)))
	# print(' '.join(list(result.stdout)))	
	trace_subnet = []
	for line in result.stdout:
		print(line)
		regex_ip = extract_ip(line)
		if regex_ip != "8.8.8.8":
			trace_subnet.append(regex_ip+'/24')
		else:
			pass
	print(trace_subnet)
	return trace_subnet

def verify(target_host):
	nm = nmap.PortScanner()
	nm.scan(hosts='target_host')
	print(nm.all_hosts())

def deep_scan(target_host):
	nm = nmap.PortScanner()
	nm.scan(hosts='target_host', arguments='-p22,80,443 -sV')
	print(nm.csv())

def probe(target_subnet):
	trace_subnet = traceroute()
	trace_subnet = trace_subnet + target_subnet
	# result = subprocess.run(['ping', '-c', '1', target_subnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print(result.stdout.decode('utf-8'))


	print("SUBNET TERIDENTIFIKASI:\t" + ', '.join(trace_subnet	))
	for trace in trace_subnet:
		print("PROBE: \t" + trace)
		probe_scan = subprocess.Popen(['masscan','-p' + str_common_ports, trace], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		for probe in probe_scan.stdout:
			print(probe)
			regex_host_ip = extract_ip(str(probe))
			if regex_host_ip:
				print("HOST FOUND: \t" + regex_host_ip + ", verifying...")
				multiprocessing.Process(target=verify, args=(regex_host_ip,)).start()
				# verify(regex_host_ip)
				# deep_scan(regex_host_ip)
			else:
				pass



def identify():
	pass

def parsearg():
	banner = "     e                 d8             ~~~~d88P ~~~888~~~ \n    d8b     888  888 _d88__  e88~-_      d88P     888    \n   /Y88b    888  888  888   d888   i    d88P      888    \n  /  Y88b   888  888  888   8888   |   d88P       888    \n /____Y88b  888  888  888   Y888   '  d88P        888    \n/      Y88b \"88_-888  \"88_/  \"88_-~  d88P____     888    \nNetwork scanner to measure Zero Trust Implementation by ReiKT. -h for help"
	print(banner)
	parser = argparse.ArgumentParser(description='Make sure masscan and nmap is installed and accessible from terminal/cmd')
	parser.add_argument('--subnet', required=False, help='Scan specific subnet')
	parser.add_argument('--threads', required=False, type=int, help='Max threads used during scanning')
	parser.add_argument('--int', required=False, help='Select NIC to perform scanning')

	args = parser.parse_args()
	if args.subnet:
		probe(args.subnet)
	else:
		probe(private_subnets)

parsearg()

# nm = nmap.PortScanner()
# nm.scan(hosts="10.10.29.131", arguments='-T5 -sV')
# print(nm.csv())

