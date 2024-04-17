import nmap
import masscan
import socket
import argparse
import subprocess
import re
# import multithreading

private_subnets = ['192.168.0.0/16', '172.16.0.0/16', '10.0.0.0/8']

def extract_ip(ip_string):
	ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

    # Use re.findall to find all matches in the input string
    matches = re.findall(ip_pattern, input_string)

    # Return the first match (if any)
    return matches[0] if matches else None
#hueeasdasdas

def traceroute():
	result = subprocess.Popen(['traceroute', '-m 3', '-S', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	# print(list(result.stdout))
	for line in result.stdout:
		print(line, end='')

def probe(target_subnet):
	traceroute()
	result = subprocess.run(['ping', '-c', '1', target_subnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(result.stdout.decode('utf-8'))
	
	mas = masscan.PortScanner() 
	mas.scan(target_subnet, ports='1-1024', arguments='--max-rate 1000') 
	print(mas.scan_result)

def scan():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	print(s.getsockname()[0])
	s.close()

def identify():
	pass

def parsearg():
	parser = argparse.ArgumentParser(description='Network scanner to measure Zero Trust Implementation')
	parser.add_argument('--subnet', required=False, help='Scan specific subnet')
	parser.add_argument('--threads', required=False, type=int, help='Max threads used during scanning')
	parser.add_argument('--int', required=False, help='Select NIC to perform scanning')

	args = parser.parse_args()
	print(args.subnet)
	if args.subnet:
		probe(args.subnet)
	else:
		probe(private_subnets[0])

parsearg()

# nm = nmap.PortScanner()
# nm.scan(hosts="10.10.29.131", arguments='-T5 -sV')
# print(nm.csv())

