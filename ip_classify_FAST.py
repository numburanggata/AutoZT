import ipaddress
import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import webbrowser
import os
import csv


def check_existing_ips(ipA, ipB):
    for a in ipA:
        for b in ipB:
            if a == b:
                return(True)
                break
            else:
                pass
            # print(a, b)
            # print('no collision ')
            # print(ipA, ipB)
    return(False)

def check_usable_host_ip(ip, subnet):
    network = ipaddress.IPv4Network(subnet, strict=False)
    network_address = network.network_address
    broadcast_address = network.broadcast_address
    # print(network_address, broadcast_address)
    # print(ip, network_address, broadcast_address)
    if str(ip) == str(network_address) or str(ip) == str(broadcast_address):
        # del subnets[subnet]
        return False
    else:
        # print(ip, broadcast_address)
        return True

def classify_subnets(ip_list):
    subnets = {}
    
    for ip in ip_list:
        ip_addr = ipaddress.ip_address(ip)
        # subnet_found = False
        
        for subnet in subnets:
            if ip_addr in subnet:
                # print(ip_addr, subnet)
                # network = ipaddress.IPv4Network(subnet, strict=False)
                # network_address = network.network_address
                # broadcast_address = network.broadcast_address
                # print(network_address, broadcast_address)
                subnets[subnet].append(ip)
            else:
                pass
                # if ip_addr == network_address or ip_addr == broadcast_address:
                    # del subnets[subnet]
                    # pass
                # else:
                    # subnets[subnet].append(ip)
                # subnet_found = True
                # print(subnets)
                
        
        # if not subnet_found:
        for cidr in range(29, 21, -1): 
            subnet = ipaddress.ip_network(f"{ip}/{cidr}", strict=False)
            # if any(ipaddress.ip_address(ip) in subnet for ip in ip_list):
            network = ipaddress.IPv4Network(subnet, strict=False)
            network_address = network.network_address
            broadcast_address = network.broadcast_address
            # print(ip, subnet, network_address, broadcast_address)
            if subnet not in subnets:
                subnets[subnet] = [ip]
                # print("subet: " + subnet + "subnets"+ )
                # print(ip, subnet, network_address, broadcast_address)
                # if ip == network_address or ip == broadcast_address:
                    # pass
                # else:
                    # subnets[subnet] = [ip]
                    # print('regist')
            else:
                pass
                # print(subnet, ip, cidr)

    # print(subnets)
    subnet_rank = []
    existing_subnets = []
    for subnet, ips in subnets.items():
        cidr = (str(subnet).split('/'))[1]
        if cidr == str(24):
            # print(f"Existing subnet {subnet}: {ips} ")
            existing_subnets.append([subnet, ips])
        available_host = ((32 - int(cidr)) ** 2) - 2 
        # print(0.85*(len(ips)/available_host))
        # print(0.15*((29-int(cidr))/7))
        subnet_rank.append([subnet, ips, ( 0.80*(len(ips)/available_host) + 0.20*((29-int(cidr))/7) )])

    #RUMUS BEST SUBNET => (used IP/possible IP) * 75% + flexibility_factor * 25% 
    # BEST SUBNET = Host Utilization (Aspek Modular, Security) + Address Utilization (Aspek Fleksibilitas, Kesederhanaan)
    # print(subnet_rank)
    # print(subnet_rank)
    sorted_subnet_rank = sorted(subnet_rank, key=lambda x: x[2], reverse=True)

    #print(sorted_subnet_rank)
    for x in sorted_subnet_rank[0][1]:
        # print(x)
        # print(sorted_subnet_rank[0][0])
        if check_usable_host_ip(x, sorted_subnet_rank[0][0]):
            # print('ok ' + x)
            pass
        else:
            # print('not usable')
            sorted_subnet_rank = sorted_subnet_rank[1:]
            break


    microsegment = [sorted_subnet_rank[0]]
    prev_ips = sorted_subnet_rank[0][1]
    # print(microsegment)
    # print(sorted_subnet_rank)

    for x in sorted_subnet_rank[1:]:
        #print(x)
        ips_collision = check_existing_ips(prev_ips, x[1])
        if ips_collision == True:
            pass 
        else:
            microsegment.append(x)
            #print(x[1])
            prev_ips = prev_ips + x[1]

    # for _ in microsegment:
        # print(_)


    ip_data = {
    "Probed Network Address": [],
    "Probed Network Hosts": [],
    "Probed Network Zone": [],
    "Recommended Network Address": [],
    "Recommended Network Hosts": []
    }

    for i, (subnet, hosts) in enumerate(existing_subnets):
        ip_data["Probed Network Address"].append(str(subnet))
        ip_data["Probed Network Hosts"].append(", ".join(hosts))
        ip_data["Probed Network Zone"].append("Unnamed")

    for recommended in microsegment:
        ip_data["Recommended Network Address"].append(str(recommended[0]))
        ip_data["Recommended Network Hosts"].append(", ".join(recommended[1]))


    # for key, value in ip_data.items():
        # print(_)
        # print(f"{key}: {value}")

    return(ip_data)


def generate_vlan_config(subnets, zones):
    config_lines = []

    vlan_id = 10  # Starting VLAN ID; adjust as needed

    config_lines.append("! Assign an interface as Trunk if needed")
    config_lines.append(f"interface Ethernetx/x")
    config_lines.append(f" switchport trunk encapsulation dot1q")
    config_lines.append(f" switchport mode trunk")
    config_lines.append(f" switchport trunk allowed vlan xx,xx")
    config_lines.append(" no shutdown")
    config_lines.append("\n")
    for index, subnet in enumerate(subnets):
        # Calculate the network address and subnet mask
        subnet_info = subnet.split('/')
        network_address = subnet_info[0]
        subnet_mask = int(subnet_info[1])

        # Determine VLAN name, defaulting to "VLAN_<vlan_id>" if the zone is empty
        vlan_name = zones[index] if index < len(zones) and zones[index] else f"VLAN_{vlan_id}"

        # Create VLAN configuration
        config_lines.append(f"vlan {vlan_id}")
        config_lines.append(f" name {vlan_name}")
        #config_lines.append("!")

        # Configure the VLAN interface
        config_lines.append(f"interface Vlan{vlan_id}")
        #config_lines.append(f" ip address {network_address} {subnet_mask_to_cidr(subnet_mask)}")
        config_lines.append(" no shutdown")
        
        
        config_lines.append("! Assign the VLAN into associated ports/interfaces")
        config_lines.append(f"interface Ethernetx/x")
        config_lines.append(f" switchport mode access")
        config_lines.append(f" switchport access vlan {vlan_id}")
        config_lines.append(" no shutdown")
        config_lines.append("\n")

        vlan_id += 1
        
    # Router Configuration
    router_config_lines = ["! Router Configuration"]
    vlan_id = 10  # Reset VLAN ID for consistency

    for index, subnet in enumerate(subnets):
        # Extract network address and prefix length
        subnet_info = subnet.split('/')
        network_address = subnet_info[0]
        subnet_prefix = int(subnet_info[1])

        # Define router IP for DHCP and inter-VLAN routing
        router_ip = calculate_router_ip(network_address, subnet_prefix)

        # Router subinterface configuration for each VLAN
        router_config_lines.append(f"interface GigabitEthernet0/0.{vlan_id}")
        router_config_lines.append(f" encapsulation dot1Q {vlan_id}")
        router_config_lines.append(f" ip address {router_ip} {subnet_prefix_to_mask(subnet_prefix)}")
        router_config_lines.append(" no shutdown")
        router_config_lines.append("")

        # DHCP Pool for each VLAN
        router_config_lines.append(f"ip dhcp pool VLAN_{vlan_id}")
        router_config_lines.append(f" network {network_address} {subnet_prefix_to_mask(subnet_prefix)}")
        router_config_lines.append(f" default-router {router_ip}")
        #router_config_lines.append(" dns-server 8.8.8.8 8.8.4.4")  # Optional: Set DNS servers
        #router_config_lines.append(" lease 7")  # Set DHCP lease time in days, optional
        router_config_lines.append("")

        vlan_id += 1

    # Combine switch and router configurations
    config_lines.extend(router_config_lines)

    return "\n".join(config_lines)


def subnet_prefix_to_mask(prefix):
    # Helper function to convert subnet prefix length (e.g., /24) to subnet mask (e.g., 255.255.255.0)
    mask = (0xffffffff >> (32 - prefix)) << (32 - prefix)
    return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    
def subnet_mask_to_cidr(mask_bits):
    # Converts subnet mask bits into a CIDR format
    bits = (0xffffffff >> (32 - mask_bits)) << (32 - mask_bits)
    return f"{(bits >> 24) & 0xff}.{(bits >> 16) & 0xff}.{(bits >> 8) & 0xff}.{bits & 0xff}"

def calculate_router_ip(network_address, prefix):
    # Calculate the router IP as the first usable address in the subnet
    ip_parts = list(map(int, network_address.split(".")))
    ip_parts[-1] += 1  # Increment last octet for first usable address
    return ".".join(map(str, ip_parts))



    # print(subnets)
    # cidr_ = ipaddress.ip_address
    # 
    # print(host_percentage)
    # return subnets


# Example usage:
#ip_list = [
    # '192.168.1.10', 
    # '192.168.1.20', 
    # '192.168.2.30',
    # '192.168.1.15', 
    # '192.168.2.40',
    #'192.168.3.1',
    #'192.168.3.2',
    #'192.168.3.3',
    #'192.168.3.4',
    #'192.168.3.5',
    #'192.168.3.6',
    #'192.168.3.7',
    #'192.168.3.9',
    #'192.168.3.10',
    #'192.168.3.11',
    #'192.168.3.12',
    #'192.168.1.1',
    #'192.168.1.2',
    #'192.168.1.3',
    #'192.168.1.4',
    #'192.168.1.5',
    #'192.168.1.6',
    #'192.168.1.7',
    #'192.168.1.9',
    #'192.168.1.10',
    #'192.168.1.11',
    #'192.168.1.12',
    #'192.168.1.13',
    #'192.168.1.14',
    #'192.168.1.15',
    #'192.168.1.16',
    #'192.168.1.17',
    #'192.168.1.19',
    #'192.168.1.20',
    #'192.168.1.21',
    #'192.168.1.22',
    # '192.168.3.221',
    # '192.168.3.223',
    # '192.168.3.225', 
    # '10.0.0.12',
    # '10.0.1.1',
    # '172.16.0.1',
    # '10.10.100.121',
    #]

# Initialize an empty list to store the first column values
ip_list = []

# Read the file and extract the first column from each row
with open("ca_temp.txt", "r") as file:
    for line in file:
        # Strip leading/trailing whitespaces and newline characters, then split by commas
        columns = line.strip().split(",")
        # Append the first column (first element) to the list
        ip_list.append(columns[0])

# Print the list of first column values
#print(first_column_list)

classified_subnets = classify_subnets(ip_list)
# for subnet, ips in classified_subnets.items():
    # print(f"Subnet {subnet}: {ips}")
# print(classified_subnets)
items = list(classified_subnets.items())
# midpoint = len(items) // 2

probed_subnets = dict(items[:3])
probed_subnets = {
    key: [value for i, value in enumerate(values) if probed_subnets['Probed Network Address'][i] and probed_subnets['Probed Network Hosts'][i]]
    for key, values in probed_subnets.items()
}
# print(probed_subnets)   
# print('items 2')
# print(items[2])


recommended_zones = [""] * len(items[3][1])
internet_only = ["inet_access"] * len(items[3][1])
    
items.append(['Network Zone', recommended_zones])
items.append(['Internet Access', internet_only])

recommended_subnets = dict(items[3:])

# print(probed_subnets, recommended_subnets)

# ip_data = {
#     "Probed Network Address": ["192.168.0.0/24", ""],
#     "Probed Network Hosts": ["192.168.0.1, 192.168.0.4, 192.168.0.232", ""],
#     "Probed Network Zone": ["ServerFarm", ""],
#     "Recommended Network Address": ["192.168.0.0/28", "192.168.0.224/28"],
#     "Recommended Network Hosts": ["192.168.0.1, 192.168.0.4", "192.168.0.232"]
# }


# print(recommended_subnets)

# recommended_subnets = {'Recommended Network Address': ['192.168.3.0/29', '192.168.1.0/29', '192.168.1.8/29', '192.168.1.16/29', '192.168.3.8/29'], 'Recommended Network Hosts': ['192.168.3.1, 192.168.3.2, 192.168.3.3, 192.168.3.4, 192.168.3.5, 192.168.3.6, 192.168.3.7', '192.168.1.1, 192.168.1.2, 192.168.1.3, 192.168.1.4, 192.168.1.5, 192.168.1.6, 192.168.1.7', '192.168.1.9, 192.168.1.10, 192.168.1.11, 192.168.1.12, 192.168.1.13, 192.168.1.14, 192.168.1.15', '192.168.1.16, 192.168.1.17, 192.168.1.19, 192.168.1.20, 192.168.1.21, 192.168.1.22', '192.168.3.9, 192.168.3.10, 192.168.3.11, 192.168.3.12']}


# Convert sample data to DataFrame
df_probed = pd.DataFrame(probed_subnets)
df_recommended = pd.DataFrame(recommended_subnets)

action_options = [
    {"label": "Internet Only", "value": "inet_only"},
    {"label": "Internet Access", "value": "inet_access"},
    {"label": "No Internet", "value": "inet_no"}
]
# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div(style={
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f0f2f5',
        'padding': '20px'
    },
    children=[
        # Header Section
        html.Div(
            style={
                'textAlign': 'center',
                'padding': '20px',
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'marginBottom': '30px'
            },
            children=[
                html.H1("Subnet Miscrosegmentation", style={'margin': '0'})
            ]
        ),

        # Probed Networks Table Section
        html.Div(
            style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'marginBottom': '30px'
            },
            children=[
                html.H2("Probed Networks", style={'textAlign': 'center', 'color': '#333'}),
                dash_table.DataTable(
                    id='probed-table',
                    columns=[
                        {"name": "Probed Network Address", "id": "Probed Network Address", "deletable": False, "renamable": False},
                        {"name": "Probed Network Hosts", "id": "Probed Network Hosts", "deletable": False, "renamable": False},
                    ],
                    data=df_probed.to_dict('records'),
                    editable=False,
                    row_deletable=False,
                    page_size=10,
                    style_table={
                        'overflowX': 'auto'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'minWidth': '200px',
                        'maxWidth': '400px',
                        'whiteSpace': 'normal',
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': '16px'
                    },
                    style_data={
                        'border': '1px solid #ddd'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        },
                        {
                            'if': {'state': 'active'},  # Active cell
                            'backgroundColor': '#d1e7dd',
                            'border': '1px solid #4CAF50'
                        }
                    ],
                    css=[
                        {
                            'selector': '.dash-spreadsheet td div',
                            'rule': 'line-height: 15px;'
                        }
                    ]
                ),
            ]
        ),

        # Recommended Networks Table Section
        html.Div(
            style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'marginBottom': '30px'
            },
            children=[
                html.H2("Recommended Networks", style={'textAlign': 'center', 'color': '#333'}),
                dash_table.DataTable(
                    id='recommended-table',
                    columns=[
                        {"name": "Recommended Network Address", "id": "Recommended Network Address", "deletable": False, "renamable": False},
                        {"name": "Recommended Network Hosts", "id": "Recommended Network Hosts", "deletable": False, "renamable": False},
                        {"name": "Network Zone", "id": "Network Zone", "deletable": False, "renamable": False},
                        {"name": "Internet Access Only?", "id": "Internet Access", "deletable": False, "renamable": False, "presentation": "dropdown"}
                    ],
                    data=df_recommended.to_dict('records'),
                    editable=True,  # Recommended networks are output only
                    row_deletable=True,
                    page_size=10,
                    dropdown={
                    'Internet Access': { 'options': action_options}
                    },
                    style_table={
                        'overflowX': 'auto'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'minWidth': '200px',
                        'maxWidth': '400px',
                        'whiteSpace': 'normal',
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': '16px'
                    },
                    style_data={
                        'border': '1px solid #ddd'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        },
                        {
                            'if': {'state': 'active'},  # Active cell
                            'backgroundColor': '#d1e7dd',
                            'border': '1px solid #4CAF50'
                        },
                       {
                            'if': {'column_id': 'Probed Network Zone'},
                            'color': 'white',
                            'backgroundColor': '#6c757d',
                            'fontWeight': 'bold'
                        }
                    ],
                    css=[
                        {
                            'selector': '.dash-spreadsheet td div',
                            'rule': 'line-height: 15px;'
                        }
                    ]
                   
		    # Add a dropdown to the new "Internet Access" column
		    #editable=True,
		    #cell_editable=True,
		    #cell_selectable=True,
		    #dropdown_conditional={
			#'if': {'column_id': 'Internet Access'},
			#'options': [
			 #   {'label': 'Yes', 'value': 'Yes'},
			  #  {'label': 'No', 'value': 'No'}
			#]
		   # }
                ),
            ]
        ),

        # Buttons Section
        html.Div(
            style={
                'textAlign': 'center',
                'marginBottom': '30px'
            },
            children=[
                html.Button('Add Row', id='add-row-btn', n_clicks=0, style={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'padding': '10px 20px',
                        'marginRight': '10px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px'
                    }),
                 
                html.Button(
                    'Classify Networks',
                    id='classify-btn',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'padding': '10px 20px',
                        'marginRight': '10px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px'
                    }
                ),
                html.Button(
                    'Exit',
                    id='exit-btn',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#FF0000',
                        'color': 'white',
                        'padding': '10px 20px',
                        'marginRight': '10px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px'
                    }
                )
            ]
        ),

        # Output Area Section
        html.Div(
            style={
                'marginTop': '30px',
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.1)'
            },
            children=[
                html.H2('Miscrosegmentation Config', style={'textAlign': 'center', 'color': '#333'}),
                html.Pre(
                    id='microseg-output',
                    style={
                        'whiteSpace': 'pre-wrap',
                        'backgroundColor': '#f9f9f9',
                        'padding': '15px',
                        'borderRadius': '5px',
                        'border': '1px solid #ddd',
                        'fontSize': '14px',
                        'maxHeight': '400px',
                        'overflowY': 'auto'
                    }
                )
            ]
        )
    ]
)

@app.callback(
    [Output('recommended-table', 'data'), Output('microseg-output', 'children')],
    [Input('add-row-btn', 'n_clicks'),Input('classify-btn', 'n_clicks'),Input('exit-btn', 'n_clicks')],
    State('recommended-table', 'data')
)

def update(add_row, classify_clicks, exit_clicks, rows):
    # print(add_row, classify_clicks, rows)
    ctx = dash.callback_context
    if not ctx.triggered:
        return None

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-row-btn': 
        if add_row > 0:
            rows.append({"Recommended Network Address": '0.0.0.0/24', "Recommended Network Hosts": '0.0.0.0', "Network Zone": ''})
            return rows, ['']
            
    if button_id == 'exit-btn': 
        if exit_clicks > 0:
            os._exit(0)
 

    elif button_id == 'classify-btn':
        if classify_clicks > 0:
            hosts = []
            zones = []
            internet_access = []
            for row in rows:
                #print(row)
                hosts_in_row = row['Recommended Network Address']
                zones.append(row['Network Zone'])
                internet_access.append(row['Internet Access'])
                if hosts_in_row:
                    hosts.extend([host.strip() for host in hosts_in_row.split(",") if host.strip()])
            vlan_config = generate_vlan_config(hosts, zones) 
            
            with open("recommended_subnets.csv", mode='w', newline='') as file:
                writer = csv.writer(file)
                csv_rows = zip(hosts, zones, internet_access)
                writer.writerow(["Recommended Network Address", "Network Zone", "Internet Access"])
                writer.writerows(csv_rows)
                
            with open('vlan_config.txt', 'w') as file:
                file.write(vlan_config)
            print(vlan_config)
            
            return rows, vlan_config
    return ""

if __name__ == '__main__':
    # Auto-open web browser
    webbrowser.open("http://127.0.0.1:8050")

    # Run the Dash app
    app.run_server(debug=False, use_reloader=False)
    
