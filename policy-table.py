import pandas as pd
from ipywidgets import interactive
from IPython.display import display

# Sample data
data = {
    "Policy Number": ["P001", "P002", "P003"],
    "Source Zone": ["Zone1", "Zone2", "Zone3"],
    "Source Address": ["192.168.1.1", "192.168.1.2", "192.168.1.3"],
    "Dest Zone": ["ZoneA", "ZoneB", "ZoneC"],
    "Dest Address": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
    "Protocol": ["TCP", "UDP", "ICMP"],
    "Port": [80, 53, 0],
    "Action": ["Allow", "Deny", "Allow"]
}

# Create DataFrame
df = pd.DataFrame(data)

def edit_table(index, policy_number, source_zone, source_address, dest_zone, dest_address, protocol, port, action):
    # Update DataFrame based on widget input
    df.loc[index] = [policy_number, source_zone, source_address, dest_zone, dest_address, protocol, port, action]
    display(df)

# Create widgets for each column
interactive_table = interactive(
    edit_table,
    index=(0, len(df) - 1),
    policy_number=[str(x) for x in df["Policy Number"]],
    source_zone=[str(x) for x in df["Source Zone"]],
    source_address=[str(x) for x in df["Source Address"]],
    dest_zone=[str(x) for x in df["Dest Zone"]],
    dest_address=[str(x) for x in df["Dest Address"]],
    protocol=[str(x) for x in df["Protocol"]],
    port=[int(x) for x in df["Port"]],
    action=[str(x) for x in df["Action"]]
)

display(interactive_table)
