from ixnetwork_restpy import SessionAssistant
import time

final_table = []
apiServerIp = '10.36.74.13'

session = SessionAssistant(IpAddress=apiServerIp, RestPort=None, UserName='admin', Password='XXX', 
                            SessionName=None, SessionId=1, ApiKey=None,
                            ClearConfig=False)


flow_stats_view = session.Ixnetwork.Statistics.find().View.find(Caption = "Flow Statistics" )
# We are getting the drilldown here. Arg2 = Row Number in view and Arg3 is value in the dropdown
flow_stats_drill_down_for_uds = flow_stats_view.DoDrillDownByOption(Arg2=1, Arg3='Ethernet:Outer VLAN ID (4 bits) at offset 124') # 'Show All Egress'

time.sleep(30) # When we do drill down on Flow Statistics it takes some time for User def stats to populate. (Only for first time)

# Now we have a tab for User Defined Statistics lets get values from that
uds_view = session.Ixnetwork.Statistics.find().View.find(Caption = "User Defined Statistics")
# Select the option for Arg2 based on the packets you want to view
uds_view.SetEgressViewMode(Arg2="kAll") # (kAll | kNotDefined | kRowsWithNoPackets | kRowsWithPackets)

final_table.append(uds_view.Data.ColumnCaptions)
for item in uds_view.Data.PageValues[0]:
    final_table.append(item)

# Making a dict of the values for ease of parsing
# Step 1: Extract the keys (column headers)
keys = final_table[0]  # First row is the header
# Step 2: Convert to a list of dictionaries
result = [dict(zip(keys, row)) for row in final_table[1:]]  # Skip the header row
print(result)


"""
Sample Output:
==============

[
    {
        "Tx Port": "10GE LAN - 001",
        "Rx Port": "10GE LAN - 002",
        "Traffic Item": "Traffic Item 1",
        "VLAN:VLAN-ID": "1",
        "Egress Tracking": "Ethernet:Outer VLAN ID (4 bits) at offset 124",
        "Tx Frames": "916086439",
        "Rx Frames": "916086435",
        "Frames Delta": "4",
        "Loss %": "0",
        "Tx Frame Rate": "2349624",
        "Rx Frame Rate": "2349624",
        "Tx L1 Rate (bps)": "9999999744",
        "Rx L1 Rate (bps)": "9999999744",
        "Rx Bytes": "469036254720",
        "Tx Rate (Bps)": "1203007488",
        "Rx Rate (Bps)": "1203007488",
        "Tx Rate (bps)": "9624059904",
        "Rx Rate (bps)": "9624059904",
        "Tx Rate (Kbps)": "9624059.904",
        "Rx Rate (Kbps)": "9624059.904",
        "Tx Rate (Mbps)": "9624.06",
        "Rx Rate (Mbps)": "9624.06",
        "Store-Forward Avg Latency (ns)": "0",
        "Store-Forward Min Latency (ns)": "0",
        "Store-Forward Max Latency (ns)": "0",
        "First TimeStamp": "00:00:00.993",
        "Last TimeStamp": "00:06:30.880"
    },
    {
        "Tx Port": "",
        "Rx Port": "",
        "Traffic Item": "",
        "VLAN:VLAN-ID": "",
        "Egress Tracking": "1",
        "Tx Frames": "",
        "Rx Frames": "916086435",
        "Frames Delta": "",
        "Loss %": "",
        "Tx Frame Rate": "",
        "Rx Frame Rate": "2349624",
        "Tx L1 Rate (bps)": "",
        "Rx L1 Rate (bps)": "9999999744",
        "Rx Bytes": "469036254720",
        "Tx Rate (Bps)": "",
        "Rx Rate (Bps)": "1203007488",
        "Tx Rate (bps)": "",
        "Rx Rate (bps)": "9624059904",
        "Tx Rate (Kbps)": "",
        "Rx Rate (Kbps)": "9624059.904",
        "Tx Rate (Mbps)": "",
        "Rx Rate (Mbps)": "9624.06",
        "Store-Forward Avg Latency (ns)": "0",
        "Store-Forward Min Latency (ns)": "0",
        "Store-Forward Max Latency (ns)": "0",
        "First TimeStamp": "00:00:00.993",
        "Last TimeStamp": "00:06:30.880"
    }
]


"""
