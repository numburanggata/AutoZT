import ipaddress
import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import webbrowser


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
        # print("FALSE GOBLOK")
        return False
    else:
        # print(ip, broadcast_address)
        # print("TRUE GOBLOK")
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
        subnet_rank.append([subnet, ips, ( 0.70*(len(ips)/available_host) + 0.30*((29-int(cidr))/7) )])

    #RUMUS BEST SUBNET => (used IP/possible IP) * 75% + flexibility_factor * 25% 
    # BEST SUBNET = Host Utilization (Aspek Modular, Security) + Address Utilization (Aspek Fleksibilitas, Kesederhanaan)
    # print(subnet_rank)
    # print(subnet_rank)
    sorted_subnet_rank = sorted(subnet_rank, key=lambda x: x[2], reverse=True)

    print(sorted_subnet_rank)
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





    # print(subnets)
    # cidr_ = ipaddress.ip_address
    # 
    # print(host_percentage)
    # return subnets


# Example usage:
ip_list = [
    # '192.168.1.10', 
    # '192.168.1.20', 
    # '192.168.2.30',
    # '192.168.1.15', 
    # '192.168.2.40',
    '192.168.3.1',
    '192.168.3.2',
    '192.168.3.3',
    '192.168.3.4',
    '192.168.3.5',
    '192.168.3.6',
    '192.168.3.7',
    '192.168.3.9',
    '192.168.3.10',
    '192.168.3.11',
    '192.168.3.12',
    '192.168.1.1',
    '192.168.1.2',
    '192.168.1.3',
    '192.168.1.4',
    '192.168.1.5',
    '192.168.1.6',
    '192.168.1.7',
    '192.168.1.9',
    '192.168.1.10',
    '192.168.1.11',
    '192.168.1.12',
    '192.168.1.13',
    '192.168.1.14',
    '192.168.1.15',
    '192.168.1.16',
    '192.168.1.17',
    '192.168.1.19',
    '192.168.1.20',
    '192.168.1.21',
    '192.168.1.22',
    # '192.168.3.221',
    # '192.168.3.223',
    # '192.168.3.225', 
    # '10.0.0.12',
    # '10.0.1.1',
    # '172.16.0.1',
    # '10.10.100.121',
    ]

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

recommended_subnets = {'Recommended Network Address': ['192.168.3.0/29', '192.168.1.0/29', '192.168.1.8/29', '192.168.1.16/29', '192.168.3.8/29'], 'Recommended Network Hosts': ['192.168.3.1, 192.168.3.2, 192.168.3.3, 192.168.3.4, 192.168.3.5, 192.168.3.6, 192.168.3.7', '192.168.1.1, 192.168.1.2, 192.168.1.3, 192.168.1.4, 192.168.1.5, 192.168.1.6, 192.168.1.7', '192.168.1.9, 192.168.1.10, 192.168.1.11, 192.168.1.12, 192.168.1.13, 192.168.1.14, 192.168.1.15', '192.168.1.16, 192.168.1.17, 192.168.1.19, 192.168.1.20, 192.168.1.21, 192.168.1.22', '192.168.3.9, 192.168.3.10, 192.168.3.11, 192.168.3.12']}


# Convert sample data to DataFrame
df_probed = pd.DataFrame(probed_subnets)
df_recommended = pd.DataFrame(recommended_subnets)

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
                html.H1("Langkah 2: Klasifikasi Subnet", style={'margin': '0'})
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
                        {"name": "Recommended Network Zone", "id": "Recommended Network Zone", "deletable": False, "renamable": False}
                    ],
                    data=df_recommended.to_dict('records'),
                    editable=True,  # Recommended networks are output only
                    row_deletable=True,
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
                    'Reset Tables',
                    id='reset-btn',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#f44336',
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

        # Output Area Section
        html.Div(
            style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '5px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
            },
            children=[
                html.H2("Classification Output", style={'textAlign': 'center', 'color': '#333'}),
                html.Pre(
                    id='output-area',
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
        # Output('probed-table', 'data'),
        Output('recommended-table', 'data')
        # Output('output-area', 'children')
    ,
    
        # Input('classify-btn', 'n_clicks'),
        # Input('reset-btn', 'n_clicks'),
        Input('add-row-btn', 'n_clicks')
    ,
    
        # State('recommended-table', 'data')
        State('recommended-table', 'data')
    
)

def add_row(n_clicks, rows):
    # print(classify_clicks, reset_clicks, add_row, rows)


    # ctx = dash.callback_context

    # if not ctx.triggered:
        # return rows

    # button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # print(rows)

    # if button_id == 'add-row-btn' and add_row > 0:
    if n_clicks > 0:

        # Append a blank row (or customize with default values)
        # new_row = {
            # "Recommended Network Address": "blank", 
            # "Recommended Network Hosts": "blank" 
 
        # }
        rows.append({"Recommended Network Address": '1', "Recommended Network Hosts": '1'})
        
        # Add the new blank row to the recommended rows
        # rows.append(new_row)
        # probed_rows, recommended_rows = 1
        # data = data.to_dict('records')
        # meh = ['']
        # Initialize empty lists for the new dictionary
        # network_addresses = []
        # network_hosts = []

        # Iterate over each entry in the original data
        # for entry in data:
            # Append the values to the respective lists
            # network_addresses.append(entry['Recommended Network Address'])
            # network_hosts.append(entry['Recommended Network Hosts'])

        # Create the new dictionary with the lists
        # formatted_data = {
            # 'Recommended Network Address': network_addresses,
            # 'Recommended Network Hosts': network_hosts
        # }

        # Now formatted_data contains the desired structure
        # print(formatted_data)
        # forma = [formatted_data]

    return rows

    # if button_id == 'classify-btn' and classify_clicks > 0:
    #     # Extract hosts from Probed Networks table
    #     hosts = []
    #     for row in rows:
    #         hosts_in_row = rows.get("Probed Network Hosts", "")
    #         if hosts_in_row:
    #             # Split by comma and strip spaces
    #             hosts.extend([host.strip() for host in hosts_in_row.split(",") if host.strip()])

    #     if not hosts:
    #         return rows, "❌ No hosts found to classify."

    #     # Perform classification
    #     subnet_classification = classify_subnets(hosts)

    #     # Update Probed Networks table (optional: could keep as is)
    #     updated_probed_data = subnet_classification["Probed Networks"]

    #     # Update Recommended Networks table
    #     updated_recommended_data = subnet_classification["Recommended Networks"]

    #     # Prepare output message
    #     output_message = "✅ Networks classified successfully."

    #     return (
    #         updated_probed_data["Probed Network Address"],
    #         updated_recommended_data["Recommended Network Address"],
    #         output_message
    #     )

    # elif button_id == 'reset-btn' and reset_clicks > 0:
    #     initial_probed_data = {
    #         "Probed Network Address": [],
    #         "Probed Network Hosts": [],
    #         "Probed Network Zone": []
    #     }

    #     initial_recommended_data = {
    #         "Recommended Network Address": [],
    #         "Recommended Network Hosts": []
    #     }

    #     output_message = "🧹 Tables have been reset."

    #     return (
    #         initial_probed_data["Probed Network Address"],
    #         initial_recommended_data["Recommended Network Address"],
    #         output_message
    #     )

    # return rows, ""

if __name__ == '__main__':
    # Auto-open web browser
    webbrowser.open("http://127.0.0.1:8050")

    # Run the Dash app
    app.run_server(debug=False, use_reloader=False)
    