import nmap
import socket
import argparse
import subprocess
import re
import multiprocessing
import time
import csv
from tabulate import tabulate
import ipaddress

private_subnets = ['192.168.0.0/16', '172.16.0.0/12', '10.1.1.0/24']

# queue = multiprocessing.Queue()
# with multiprocessing.Manager() as manager:
	# hosts = manager.dict()
	# hosts['sample'] = [
		# {"ip": "x.x.x.x", "state": "up", "ports": ("21 (VSFTPD)" , "22 (SSHD)")}
	# ]

with open('ca_temp.txt', 'a') as f:
	f.write("")	

with open('15common_ports.txt', 'r') as file:
    # Read the lines of the file and store them as elements in a list
    common_ports = file.readlines()
str_common_ports = [ports.strip() for ports in common_ports]
str_common_ports = ', '.join(str_common_ports)
# print (str_common_ports)

def show_ca_result():
	with open('ca_temp.txt', 'r') as f:
		reader = csv.reader(f)
		data = [row for row in reader if row]
	headers = ["IP", "State", "Ports"]
	table = tabulate (data, headers, tablefmt="grid")
	print(table)

def extract_ip(ip_string):
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    # Use re.findall to find all matches in the input string
    matches = re.findall(ip_pattern, ip_string)

    # Return the first match (if any)
    if matches:
    	return matches[0] 

def traceroute(): #AKAN DIBUAT PARALEL DGN MULTITHREADING
	print("INISIASI TRACEROUTE...")
	result = subprocess.Popen(['traceroute', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #LINUX
	# result = subprocess.Popen(['tracert','-h','3','-w','1','-d','8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #WINDOWS
	# print(list(result.stdout))
	# match = extract_ip(' '.join(list(result.stdout)))
	# print(' '.join(list(result.stdout)))	
	trace_subnet = []
	for line in result.stdout:
		print(line)
		regex_ip = extract_ip(line)
		if regex_ip:
			if regex_ip != "8.8.8.8" and regex_ip+'/24' not in trace_subnet:
				trace_subnet.append(regex_ip+'/24')
			else:
				pass
	print(trace_subnet)
	return trace_subnet

def verify(target_host):
	# print(target_host)
	nm = nmap.PortScanner()
	nm.scan(hosts=target_host)
	if nm.all_hosts():
		#hosts[target_host] = {
		#	"ip": target_host, 
		#	"state": "up", 
		#	"ports": None
		#}
		#with open('ca_temp.txt', 'a') as f:
		#	f.write(f"{target_host},up,<deep scanning...>\n")
		#found_host = {"ip": target_host, "state": "up", "ports": None}
		#hosts.append(found_host)
		print(target_host + " is UP, performing deep scan.")
		deep_scan(target_host)
		#print("HOSTS: \t", hosts)
		
	else:
		#hosts[target_host] = {
		#	"ip": target_host, 
		#	"state": "down", 
		#	"ports": None
		#}
		with open('ca_temp.txt', 'a') as f:
			f.write(f"{target_host},filtered,-\n")
		#found_host = {"ip": target_host, "state": "down", "ports": None}
		#hosts.append(found_host)
		print(target_host + " is likely DOWN")
		show_ca_result()
		#print("HOSTS: \t", hosts)
		

def deep_scan(target_host):
	nm = nmap.PortScanner()
	nm.scan(hosts=target_host, arguments='-T4 -p- --open')
	results = []
	for protocol in nm[target_host].all_protocols():
		ports = nm[target_host][protocol].keys()
		for port in sorted(ports):
			service = nm[target_host][protocol][port]['name']
			state = nm[target_host][protocol][port]['state']
			if state == "open":
				results.append(f"{port}({service})")
	format_result = ";".join(results)
	with open('ca_temp.txt', 'a') as f:
		f.write(f"{target_host},up,{format_result}\n")
	show_ca_result()

def probe(target_subnet):
	# trace_subnet = traceroute()   ## BYPASS 
	trace_subnet = ['192.168.88.153/24']
	trace_subnet = trace_subnet + target_subnet
	# result = subprocess.run(['ping', '-c', '1', target_subnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print(result.stdout.decode('utf-8'))

	print("SUBNET TERIDENTIFIKASI:\t" + ', '.join(trace_subnet	))
	
	
	for trace in trace_subnet:
		print("PROBE: \t" + trace)
		#print("HOSTS: \t", hosts)
		#for host in hosts.values():
		#	print(host)
		probe_scan = subprocess.Popen(['sudo', 'masscan','-p' + str_common_ports, trace], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#stdout, stderr = probe_scan.communicate()
		#if probe_scan.returncode != 0:
		# print((probe_scan.stderr).decode('utf-8'))
		last_probe_time = time.time()
		processes = []
		probe_counter = 0
		while True:
			output = probe_scan.stdout.readline()
			# print('1')
			if output:
				probe_counter += 1
				probe_time = time.time()
				probe_check = probe_time - last_probe_time
				# print(probe_check, probe_time, last_probe_time)
				if probe_check <= 1 and probe_counter == 10:
					print('Failed Probe, moving on...')
					for p in processes:
						if p.is_alive():  # Check if the process is still running
							p.terminate()  # Terminate the process
							p.join()  # Clean up the process resources
					break
				# print(output.strip().decode())
				regex_host_ip = extract_ip(str(output.strip().decode()))
				# print(regex_host_ip)
				if regex_host_ip:
					#host_exist = any(host["ip"] == regex_host_ip for host in hosts)
					host_exist = False
					with open('ca_temp.txt', 'r') as f:
						for line in f:
							ip, _, _ = line.strip().split(',')
							if ip == regex_host_ip:
								host_exist = True
					if host_exist:
						pass
					else:
						print("HOST FOUND: \t" + regex_host_ip + ", verifying...")
						host_state = multiprocessing.Process(target=verify, args=(regex_host_ip,))
						host_state.start()
						# print('process started')
						processes.append(host_state)
						#verify(regex_host_ip)
						# print('process appended')
						# verify(regex_host_ip)
						# deep_scan(regex_host_ip)
				else:
					pass
			
			if probe_scan.poll() is not None:
				print("PROBE SUBNET BERIKUTNYA...")
				#show_ca_result()
				break
		for p in processes:
				p.join()

	print("PROBE SUBNET SELESAI")

def classify_subnets():
	subnets = {}
	with open('ca_temp.txt', 'r') as f:
		reader = csv.reader(f)
		data = [row for row in reader if row]

	for ip in data:
		ip_addr = ipaddress.ip_address(ip[0])
		# subnet_found = False
		for subnet in subnets:
			if ip_addr in subnet:
				#print(ip_addr, subnet)
				subnets[subnet].append(ip[0])
				# subnet_found = True
				# print(subnets)
      
        # if not subnet_found:
		for cidr in range(29, 21, -1): 
			subnet = ipaddress.ip_network(f"{ip[0]}/{cidr}", strict=False)
			# if any(ipaddress.ip_address(ip) in subnet for ip in ip_list):
			if subnet not in subnets:
				subnets[subnet] = [ip[0]]
			else:
				pass
				# print(subnet, ip, cidr)

	#print(subnets.items())
	confidence = {}
	for subnet, ips in subnets.items():
		#print(subnet, ips)
		cidr = (str(subnet).split('/'))[1]
		available_host = ((32 - int(cidr)) ** 2) - 2 
		confid = 100*(len(ips)/available_host)
		confidence[subnet] = confid
		print(f"Subnet {subnet}: {ips} " + str(confid) + "%")
	print(max(confidence))
	# cidr_ = ipaddress.ip_address
	# 
	# print(host_percentage)
	# return subnets


def parsearg():
	banner = "     e                 d8             ~~~~d88P ~~~888~~~ \n    d8b     888  888 _d88__  e88~-_      d88P     888    \n   /Y88b    888  888  888   d888   i    d88P      888    \n  /  Y88b   888  888  888   8888   |   d88P       888    \n /____Y88b  888  888  888   Y888   '  d88P        888    \n/      Y88b \"88_-888  \"88_/  \"88_-~  d88P____     888    \nAutomated Zero Trust Architecture by ReiKT. -h for help"
	print(banner)
	parser = argparse.ArgumentParser(description='Make sure masscan and nmap is installed and accessible from terminal/cmd')
	parser.add_argument('--subnet', required=False, help='Scan specific subnet')
	parser.add_argument('--threads', required=False, type=int, help='Max threads used during scanning')
	parser.add_argument('--int', required=False, help='Select NIC to perform scanning')

	args = parser.parse_args()
	if args.subnet:
		probe(args.subnet)
		classify_subnets()
	else:
		probe(private_subnets)
		classify_subnets()



if __name__ == "__main__":
	parsearg()

# nm = nmap.PortScanner()
# nm.scan(hosts="10.10.29.131", arguments='-T5 -sV')
# print(nm.csv())

