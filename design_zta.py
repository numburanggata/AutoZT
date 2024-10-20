import dash
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import webbrowser
import ipaddress

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
    {"label": "ANY", "value": "ANY"}
]

action_options = [
    {"label": "PERMIT", "value": "PERMIT"},
    {"label": "DENY", "value": "DENY"}
]

df = pd.DataFrame(data)

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
                html.H1("Langkah 3: Design ZTA", style={'margin': '0'})
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
            print("Policies exported to 'cisco_acl.txt'")
            return acl_commands
    
    return ""

def export_to_cisco_acl(rows):
    """Convert each row to Cisco ACL syntax and save to a file."""
    acl_commands = []
    seq_number = 100  # Start sequence number

    for row in rows:
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

        port = row["Port"]
        
        # Construct the ACL command in extended IP access-list format
        if port != 0 and port != "ANY":  # If there's a port number, include it in the ACL command
            acl_command = f"{seq_number} {action} {protocol} {src_network_address} {src_subnet_mask} {dst_network_address} {dst_subnet_mask} eq {port}"
        elif port == "ANY":
            acl_command = f"{seq_number} ip {protocol} {src_network_address} {src_subnet_mask} {dst_network_address} {dst_subnet_mask}"
        else:
            acl_command = f"{seq_number} ip {protocol} {src_network_address} {src_subnet_mask} {dst_network_address} {dst_subnet_mask}"

        acl_commands.append(acl_command)
        seq_number += 2  # Increment sequence number by 5

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
