import dash
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import webbrowser

data = {
    "Policy Number": ["P001", "P002", "P003"],
    "Source Zone": ["Zone1", "Zone2", "Zone3"],
    "Source Address": ["192.168.1.1", "192.168.1.2", "192.168.1.3"],
    "Dest Zone": ["ZoneA", "ZoneB", "ZoneC"],
    "Dest Address": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
    "Protocol": ["TCP", "UDP", "ICMP"],
    "Port": [80, 53, 0],
    "Action": ["Permit", "Deny", "Permit"]
}

df = pd.DataFrame(data)

app = dash.Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='editable-table',
        columns=[{"name": i, "id": i, "deletable": False, "renamable": False} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        row_deletable=True,
        page_size=10
    ),
    html.Button('Save Changes', id='save-btn', n_clicks=0),
    html.Button('Export to Cisco ACL', id='export-btn', n_clicks=0),
    dcc.Store(id='memory-output'),
    html.Pre(id='acl-output', style={'whiteSpace': 'pre-wrap'})  # To display the ACL output
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
        dst_address = row["Dest Address"]
        port = row["Port"]
        
        # Construct the ACL command in extended IP access-list format
        if port != 0:  # If there's a port number, include it in the ACL command
            acl_command = f"{seq_number} {action} {protocol} {src_address} any eq {port} {dst_address} any"
        else:
            acl_command = f"{seq_number} {action} {protocol} {src_address} any {dst_address} any"
        
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
