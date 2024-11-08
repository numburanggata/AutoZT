import dash
from dash import dash_table, dcc, html, Input, Output, State
import pandas as pd

# Sample DataFrame
recommended_subnets = {'Recommended Network Address': ['192.168.3.0/29', '192.168.1.0/29', '192.168.1.8/29', '192.168.1.16/29', '192.168.3.8/29'], 'Recommended Network Hosts': ['192.168.3.1, 192.168.3.2, 192.168.3.3, 192.168.3.4, 192.168.3.5, 192.168.3.6, 192.168.3.7', '192.168.1.1, 192.168.1.2, 192.168.1.3, 192.168.1.4, 192.168.1.5, 192.168.1.6, 192.168.1.7', '192.168.1.9, 192.168.1.10, 192.168.1.11, 192.168.1.12, 192.168.1.13, 192.168.1.14, 192.168.1.15', '192.168.1.16, 192.168.1.17, 192.168.1.19, 192.168.1.20, 192.168.1.21, 192.168.1.22', '192.168.3.9, 192.168.3.10, 192.168.3.11, 192.168.3.12']}
df_probed = pd.DataFrame(recommended_subnets)

app = dash.Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='probed-table',
        columns=[
            {"name": "Recommended Network Address", "id": "Recommended Network Address", "deletable": False, "renamable": False},
            {"name": "Recommended Network Hosts", "id": "Recommended Network Hosts", "deletable": False, "renamable": False},
            {"name": "a Network Hosts", "id": "a Network Hosts", "deletable": False, "renamable": False}
        ],
        data=df_probed.to_dict('records'),
        editable=True,
        row_deletable=True,
        page_size=10,
    ),
    html.Button("Add Row", id="add-row-button", n_clicks=0),
    # dcc.Input(id='new-address', placeholder="Enter Network Address", type="text"),
    # dcc.Input(id='new-hosts', placeholder="Enter Number of Hosts", type="number"),
])

@app.callback(
    Output('probed-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('probed-table', 'data'),
    # State('new-address', 'value'),
    # State('new-hosts', 'value')
)
def add_row(n_clicks, rows):
    print(rows)
    if n_clicks > 0:
        rows.append({"Recommended Network Address": '1', "Recommended Network Hosts": '1'})
        
    return rows

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
