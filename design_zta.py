import dash
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import webbrowser
import ipaddress
import csv

def get_ports_for_ip(ip_address, csv_file_path):

    ports = set()  # To store unique port numbers
    ip_obj = ipaddress.ip_address(ip_address)  # Convert the given IP to an IP object for comparison

    # Open the CSV file and read its content
    with open(csv_file_path, mode='r') as file:
        for line in file:
            host, subnet, status, port_data = line.strip().split(',')
            subnet_obj = ipaddress.ip_network(subnet, strict=False)  # Convert subnet to an IP network object
            
            # Check if the IP address is within this subnet
            if ip_obj in subnet_obj:
                # Extract ports from the port_data field
                if port_data and port_data != '-':
                    for entry in port_data.split(';'):
                        port = entry.split('(')[0].strip()  # Extract port number (before parentheses)
                        if port.isdigit():  # Check if it's a valid port number
                            ports.add(port)

    return sorted(ports)




data = {
    "Policy Number": ["01", "02", "03", "04", "05", "06"],
    "Source Zone": ["Internet", "Internet", "Staff", "Staff", "Serverfarm", "Serverfarm"],
    "Source Address": ["0.0.0.0/0","0.0.0.0/0", "192.168.1.0/24","192.168.1.0/24", "192.168.100.0/24","192.168.100.0/24"],
    "Dest Zone": ["Serverfarm", "Staff", "Internet", "Serverfarm", "Staff", "Internet"],
    "Dest Address": ["192.168.100.0/24", "192.168.1.0/24", "0.0.0.0/0", "192.168.100.0/24","192.168.1.0/24", "0.0.0.0/0"],
    "Protocol": ["TCP", "UDP", "ICMP","ANY", "ANY", "ANY"],
    "Port": ["80,443", "53", "0", "ANY", "ANY", "ANY"],
    "Action": ["PERMIT", "DENY", "PERMIT","DENY","DENY","DENY"]
}

protocol_options = [
    {"label": "TCP", "value": "TCP"},
    {"label": "UDP", "value": "UDP"},
    {"label": "ICMP", "value": "ICMP"},
    {"label": "IP", "value": "IP"}
]

action_options = [
    {"label": "PERMIT", "value": "PERMIT"},
    {"label": "DENY", "value": "DENY"}
]


recommended_networks = []
network_zones = []
internet_only = []

with open('recommended_subnets.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        recommended_networks.append(row['Recommended Network Address'])
        network_zones.append(row['Network Zone'])
        internet_only.append(row['Internet Access'])

recommended_policy = {
    "Policy Number": [],
    "Source Zone": [],
    "Source Address": [],
    "Dest Zone": [],
    "Dest Address": [],
    "Protocol": [],
    "Port": [],
    "Action": []
}
policy_number = 1
for subnet_src, zones_src, inet_src in zip(recommended_networks, network_zones, internet_only):
        inet_policy = 0
        for subnet_dest, zones_dest, inet_dest in zip(recommended_networks, network_zones, internet_only):
            
            #print(zones_src, zones_dest)
            if subnet_src == subnet_dest:
                #print('Same Subnet')
                continue
            if inet_src == 'inet_only':
                #if inet_policy >= 1:
                   #continue
                #print(subnet_src, zones_src, inet_src, subnet_dest, zones_dest, inet_dest)
                recommended_policy["Policy Number"].append(f"{policy_number:02d}")
                recommended_policy["Source Zone"].append(zones_src)
                recommended_policy["Source Address"].append(subnet_src)
                recommended_policy["Dest Zone"].append("Internet")
                recommended_policy["Dest Address"].append("0.0.0.0/0")  # Destination for internet
                recommended_policy["Protocol"].append("IP")  # Default protocol
                recommended_policy["Port"].append("ANY")      # Default port
                recommended_policy["Action"].append("PERMIT") # Action for allowed access
                policy_number += 1
                break
                
            #if inet_src == 'inet_no':
                
            ports = get_ports_for_ip(subnet_dest[:-3], "ca_temp.txt")
                #print("Ports for the IP address:", subnet_dest[:-3], ports) 
            port_string = ', '.join(ports)
            recommended_policy["Policy Number"].append(f"{policy_number:02d}")
            recommended_policy["Source Zone"].append(zones_src)
            recommended_policy["Source Address"].append(subnet_src)
            recommended_policy["Dest Zone"].append(zones_dest)
            recommended_policy["Dest Address"].append(subnet_dest)  # Destination for internet
            recommended_policy["Protocol"].append("IP")  # Default protocol
            recommended_policy["Port"].append(port_string)      # Default port
            recommended_policy["Action"].append("PERMIT") # Action for allowed access
                
            policy_number += 1
            inet_policy += 1
            print(inet_policy, len(network_zones))

            if inet_src == 'inet_access' and inet_policy + 1 >= len(network_zones):
                #if inet_policy >= 1:
                   #continue
                #print(subnet_src, zones_src, inet_src, subnet_dest, zones_dest, inet_dest)
                recommended_policy["Policy Number"].append(f"{policy_number:02d}")
                recommended_policy["Source Zone"].append(zones_src)
                recommended_policy["Source Address"].append(subnet_src)
                recommended_policy["Dest Zone"].append("Internet")
                recommended_policy["Dest Address"].append("0.0.0.0/0")  # Destination for internet
                recommended_policy["Protocol"].append("IP")  # Default protocol
                recommended_policy["Port"].append("ANY")      # Default port
                recommended_policy["Action"].append("PERMIT") # Action for allowed access
                policy_number += 1
                
                

print(recommended_policy)            

df = pd.DataFrame(recommended_policy)

app = dash.Dash(__name__)

app.layout = html.Div(

    style={
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f0f2f5',
        'padding': '20px'
    },
    children=[
        # Title Section
        html.Div(
            style={
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'marginBottom': '20px'
            },
            children=[
                html.H1("Design ZTA", style={'margin': '0'})
            ]
        ),
    html.Div(
            style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
            },
            children=[
            dash_table.DataTable(
                id='editable-table',
                columns=[
                    {"name": "No.", "id": "Policy Number", "deletable": False, "renamable": False},
                    {"name": "Source Zone", "id": "Source Zone", "deletable": False, "renamable": False},
                    {"name": "Source Address", "id": "Source Address", "deletable": False, "renamable": False},
                    {"name": "Dest Zone", "id": "Dest Zone", "deletable": False, "renamable": False},
                    {"name": "Dest Address", "id": "Dest Address", "deletable": False, "renamable": False},
                    {"name": "Protocol", "id": "Protocol", "deletable": False, "renamable": False, "presentation": "dropdown"},
                    {"name": "Port", "id": "Port", "deletable": False, "renamable": False},
                    {"name": "Action", "id": "Action", "deletable": False, "renamable": False, "presentation": "dropdown"}
                ],
                data=df.to_dict('records'),
                dropdown={
                    'Protocol': { 'options': protocol_options},
                    'Action': { 'options': action_options}
                },
                editable=True,
                row_deletable=True,
                page_size=10,
                style_table={
                        'overflowX': 'auto'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'minWidth': '100px',
                        'maxWidth': '180px',
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
                            'if': {'column_id': 'Action'},
                            'color': 'white',
                            'backgroundColor': '#add8e6',
                            'fontWeight': 'bold'
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
    html.Div(
            style={
                'marginTop': '20px',
                'textAlign': 'center'
            },
            children=[
                html.Button(
                    'Save Changes',
                    id='save-btn',
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
                    'Export to Cisco ACL',
                    id='export-btn',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#008CBA',
                        'color': 'white',
                        'padding': '10px 20px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px'
                    }
                )
            ]
        ),
        
        # Output Section
        html.Div(
            style={
                'marginTop': '30px',
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.1)'
            },
            children=[
                html.H2("ACL Output", style={'textAlign': 'center', 'color': '#333'}),
                html.Pre(
                    id='acl-output',
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
    ])

@app.callback(
    Output('acl-output', 'children'),
    [Input('save-btn', 'n_clicks'), Input('export-btn', 'n_clicks')],
    State('editable-table', 'data')
)

def handle_buttons(save_clicks, export_clicks, rows):
    ctx = dash.callback_context
    if not ctx.triggered:
        return None

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'save-btn':
        if save_clicks > 0:
            updated_df = pd.DataFrame(rows)
            updated_df.to_csv('updated_table.csv', index=False)
            print("Changes saved to 'updated_table.csv'")
    
    elif button_id == 'export-btn':
        if export_clicks > 0:
            acl_commands = export_to_cisco_acl(rows)
            print(acl_commands)
            print("Policies exported to 'cisco_acl.txt'")
            return acl_commands
    
    return ""
def netmask_to_wildcard(netmask):
    # Split the netmask into a list of integers
    netmask_parts = netmask.split('.')
    
    # Convert each part into an integer
    netmask_parts = [int(part) for part in netmask_parts]
    
    # Subtract each part of the netmask from 255 to get the wildcard mask
    wildcard_parts = [255 - part for part in netmask_parts]
    
    # Join the wildcard parts into a string and return it
    return '.'.join(map(str, wildcard_parts))

def export_to_cisco_acl(rows):
    """Convert each row to Cisco ACL syntax and save to a file."""
    acl_commands = []
    #seq_number = 100  # Start sequence number

    # Group rows by Source Zone
    zones = {}
    for row in rows:
        src_zone = row['Source Zone']
        if src_zone not in zones:
            zones[src_zone] = []
        zones[src_zone].append(row)

    # Generate ACL commands for each zone
    # Generate ACL commands for each zone
    for zone, zone_rows in zones.items():
        seq_number = 100
        acl_commands.append(f"ip access-list extended VLAN-{zone}")
        
        #print(sum(element.count(src_zone) for element in row['Source Zone']))
        #Explicit deny private network access
        src_address = zone_rows[0]["Source Address"]
        src_network = ipaddress.IPv4Network(src_address, strict=False)
        src_network_address = str(src_network.network_address)
        src_subnet_mask = str(src_network.netmask)
        acl_commands.append(f"{seq_number} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 10.0.0.0 0.255.255.255")
        acl_commands.append(f"{seq_number+1} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 172.16.0.0 0.15.255.255")
        acl_commands.append(f"{seq_number+2} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 192.168.0.0 0.0.255.255")

          
        for row in zone_rows:
            action = row["Action"].lower()  # Convert to lowercase for Cisco syntax
            protocol = row["Protocol"].lower()
            src_address = row["Source Address"]
            src_network = ipaddress.IPv4Network(src_address, strict=False)
            src_network_address = str(src_network.network_address)
            src_subnet_mask = str(src_network.netmask)
            
            dst_address = row["Dest Address"]
            dst_network = ipaddress.IPv4Network(dst_address, strict=False)
            dst_network_address = str(dst_network.network_address)
            dst_subnet_mask = str(dst_network.netmask)

            ports = row["Port"]
            if ports != "ANY":
                # If ports are specified, convert them into a comma-separated string
                ports_all = list(set(ports.split(', ')))
                ports_all.sort()
                protocol = "tcp"
            
            if dst_address != "0.0.0.0/0":
                #print(dst_address)
                # Handle other destination addresses (including private subnets)
                if ports != "ANY":
                    ports_all = list(set(ports.split(', ')))
                    ports_all.sort()
                    for p in ports_all:
                        acl_command = f"{seq_number} {action} {protocol} {src_network_address} {netmask_to_wildcard(src_subnet_mask)} {dst_network_address} {netmask_to_wildcard(dst_subnet_mask)} eq {p}"
                    #acl_command = f"{seq_number} {action} {protocol} {src_network_address} {src_subnet_mask} {dst_network_address} {dst_subnet_mask} eq {ports}"
                        acl_commands.append(acl_command)
                        seq_number += 2  # Increment sequence number by 2 for each rule
                else:
                    acl_command = f"{seq_number} {action} {protocol} {src_network_address} {netmask_to_wildcard(src_subnet_mask)} {dst_network_address} {netmask_to_wildcard(dst_subnet_mask)}"
                    acl_commands.append(acl_command)
                    seq_number += 2  # Increment sequence number by 2 for each rule
            # If the destination is "Internet", deny access to private subnets and allow all traffic to the internet
            else:
               #print(sum(element.count(src_zone) for element in recommended_policy["Source Zone"]))
                #if sum(element.count(src_zone) for element in recommended_policy["Source Zone"]) > 1:
                   #print(sum(element.count(src_zone) for element in row['Source Zone']))
                    #Deny private network access
                #    acl_commands.append(f"{seq_number} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 10.0.0.0 0.255.255.255")
                #    acl_commands.append(f"{seq_number+1} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 172.16.0.0 0.15.255.255")
                #    acl_commands.append(f"{seq_number+2} deny ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} 192.168.0.0 0.0.255.255")
                acl_commands.append(f"{seq_number+3} permit ip {src_network_address} {netmask_to_wildcard(src_subnet_mask)} {dst_network_address} {netmask_to_wildcard(dst_subnet_mask)}")
                seq_number += 4  # Increment sequence by 4 for these rules
                        
        # Add the ACL application to the relevant interface
        acl_commands.append(f"interface FastEthernetx/x")
        acl_commands.append(f"ip access-group VLAN-{zone} in")
        acl_commands.append("")  # Add an empty line for clarity between different ACLs
    
    # Save ACL commands to a file
    with open('cisco_acl.txt', 'w') as file:
        for command in acl_commands:
            file.write(command + '\n')

    return '\n'.join(acl_commands)

if __name__ == '__main__':
    # Auto-open web browser
    webbrowser.open("http://127.0.0.1:8050")

    # Run the Dash app
    app.run_server(debug=False, use_reloader=False)
