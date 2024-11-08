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

def classify_subnets(ip_list):
    subnets = {}
    
    for ip in ip_list:
        ip_addr = ipaddress.ip_address(ip)
        # subnet_found = False
        
        for subnet in subnets:
            if ip_addr in subnet:
                #print(ip_addr, subnet)
                subnets[subnet].append(ip)
                # subnet_found = True
                # print(subnets)
                
        
        # if not subnet_found:
        for cidr in range(29, 21, -1): 
            subnet = ipaddress.ip_network(f"{ip}/{cidr}", strict=False)
            # if any(ipaddress.ip_address(ip) in subnet for ip in ip_list):
            if subnet not in subnets:
                subnets[subnet] = [ip]
            else:
                pass
                # print(subnet, ip, cidr)

    # print(subnets)
    subnet_rank = []
    existing_subnets = []
    for subnet, ips in subnets.items():
        cidr = (str(subnet).split('/'))[1]
        if cidr == str(24):
            print(f"Existing subnet {subnet}: {ips} ")
            existing_subnets.append([subnet, ips])
        available_host = ((32 - int(cidr)) ** 2) - 2 
        #print(50*(len(ips)/available_host)/100)
        #print(50*((29-int(cidr))/9)/100)
        subnet_rank.append([subnet, ips, ( 75*(len(ips)/available_host)/100 + 25*((29-int(cidr))/9)/100 )])

    #RUMUS BEST SUBNET => (used IP/possible IP) * 75% + flexibility_factor * 25% 
    # BEST SUBNET = Host Utilization (Aspek Modular, Security) + Address Utilization (Aspek Fleksibilitas, Kesederhanaan)

    sorted_subnet_rank = sorted(subnet_rank, key=lambda x: x[2], reverse=True)

    microsegment = [sorted_subnet_rank[0]]
    prev_ips = sorted_subnet_rank[0][1]

    for x in sorted_subnet_rank[1:]:
        #print(x)
        ips_collision = check_existing_ips(prev_ips, x[1])
        if ips_collision == True:
            pass 
        else:
            microsegment.append(x)
            #print(x[1])
            prev_ips = prev_ips + x[1]

    for _ in microsegment:
        print(_)


# for i, (subnet, hosts) in enumerate(existing_subnets):
#     ip_data["Probed Network Address"].append(str(subnet))
#     ip_data["Probed Network Hosts"].append(", ".join(hosts))
#     ip_data["Probed Network Zone"].append(zones[i % len(zones)])
# for recommended in recommended_subnets:
#         recommended_subnet = str(recommended[0])
#         recommended_hosts = ", ".join(recommended[1])


ip_data = {
    "Probed Network Address": ["192.168.0.0/24", ""],
    "Probed Network Hosts": ["192.168.0.1, 192.168.0.4, 192.168.0.232", ""],
    "Probed Network Zone": ["ServerFarm", ""],
    "Recommended Network Address": ["192.168.0.0/28", "192.168.0.224/28"],
    "Recommended Network Hosts": ["192.168.0.1, 192.168.0.4", "192.168.0.232"]
}

# Convert sample data to DataFrame
df_classification = pd.DataFrame(ip_data)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("IP Classification Table"),
    dash_table.DataTable(
        id='classification-table',
        columns=[{"name": i, "id": i} for i in df_classification.columns],
        data=df_classification.to_dict('records'),
        editable=True,
        row_deletable=True,
        page_size=10
    ),
    html.Button('Classify Networks', id='classify-btn', n_clicks=0),
    html.Pre(id='output-area', style={'whiteSpace': 'pre-wrap'})
])

@app.callback(
    Output('output-area', 'children'),
    Input('classify-btn', 'n_clicks'),
    State('classification-table', 'data')
)
def update_output(n_clicks, rows):
    if n_clicks > 0:
        # Extract hosts from table data and classify
        hosts = []
        for row in rows:
            probed_hosts = row["Probed Network Hosts"].split(", ")
            hosts.extend(probed_hosts)

        # Perform classification
        subnet_classification = classify_subnets(hosts)

        # Format output to display in the web app
        result_output = ""
        for subnet, ips in subnet_classification.items():
            result_output += f"Subnet {subnet}: {', '.join(ips)}\n"
        
        return result_output

if __name__ == '__main__':
    # Auto-open web browser
    webbrowser.open("http://127.0.0.1:8050")

    # Run the Dash app
    app.run_server(debug=False, use_reloader=False)
    
    # print(subnets)
    # cidr_ = ipaddress.ip_address
    # 
    # print(host_percentage)
    # return subnets


# Example usage:
ip_list = [
    '192.168.1.10', 
    '192.168.1.20', 
    '192.168.2.30',
    '192.168.1.15', 
    '192.168.2.40',
    '192.168.3.1',
    '192.168.3.2',
    '192.168.3.3',
    '192.168.3.10', 
    '10.0.0.1']

classified_subnets = classify_subnets(ip_list)
# for subnet, ips in classified_subnets.items():
    # print(f"Subnet {subnet}: {ips}")
