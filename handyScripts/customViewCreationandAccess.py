"""
Note: Needs ixnetwork_restpy >= 1.1.8
Creates a layer 2-3 traffic flow custom view
This sample requires a running ixnetwork instance that has traffic being transmitted.
It uses all possible traffic filters, port filters, enumeration filters and statistics when creating the view.
The last step prior to getting data should be to enable the view.
"""

from time import sleep
from ixnetwork_restpy import SessionAssistant


session_assistant = SessionAssistant(
    IpAddress="10.36.236.121",
    UserName="admin",
    Password="Kimchi123Kimchi123!",
    LogLevel=SessionAssistant.LOGLEVEL_INFO,
    ClearConfig=False,
    SessionId=39
)
ixnetwork = session_assistant.Ixnetwork


# remove the view if it already exists
caption = "Ashwin Custome Egress View"
view = ixnetwork.Statistics.View.find(Caption=caption)

# Get the Views object
views = ixnetwork.Statistics.View.find()

# Get the page object containing row values
page = view.Page

# Get header column values
header = page.ColumnCaptions
# Get row values
row_values = page.RowValues



from tabulate import tabulate
tabl = []
tabl.append(header)

table_first_entry = []

for key, ti in row_values.items():
    for individual_egress_tracking in ti:
        if individual_egress_tracking[0]: # means it is first master row
            tabl.append(individual_egress_tracking)
        else:
            tabl.append(individual_egress_tracking) # means these are egress rows
    break

t= tabulate(tabl, tablefmt="grid")
print(t)

# if len(view) == 1:
#     view.remove()

# # create traffic flow custom view
# view = ixnetwork.Statistics.View.add(Caption=caption, Type="layer23TrafficFlow", Visible=True)

# # set filters
# l23_traffic_flow_filter = view.Layer23TrafficFlowFilter.find()

# # iterate over the TrafficItemFilters and enable them
# for traffic_item_filter in l23_traffic_flow_filter.TrafficItemFilters.find():
#     # prints the name of the port filter
#     print(traffic_item_filter.Name)
#     # set the port filter to True to enable it
#     traffic_item_filter.Enabled = True

# # iterate over the PortFilters and enable them
# for port_filter in l23_traffic_flow_filter.PortFilters.find():
#     # prints the name of the port filter
#     print(port_filter.Name)
#     # set the port filter to True to enable it
#     port_filter.Enabled = True

# # iterate over the EnumerationFilters and enable them
# for enumeration_filter in l23_traffic_flow_filter.EnumerationFilters.find():
#     # prints the name of the port filter
#     print(enumeration_filter.Name)
#     # set the port filter to True to enable it
#     enumeration_filter.Enabled = True

# # enable egress latency bin

# l23_traffic_flow_filter.EgressLatencyBinDisplayOption = "showEgressRows"

# # enable statistics
# for statistic in view.Statistic.find():
#     # prints the statistics name
#     print(statistic.Caption)
#     statistic.Enabled = True

# # enable the view
# view.Enabled = True

# # wait for data to become available
# attempts = 0
# while view.Data.IsReady is False and attempts < 10:
#     sleep(1)
#     attempts += 1

# # print the column headers
# print(" ".join(view.Data.ColumnCaptions))

# # print the snapshot data
# for data in view.Data.PageValues:
#     for row in data:
#         print(" ".join(row))
