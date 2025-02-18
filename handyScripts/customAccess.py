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
    Password="XXXXXXXXXXX!",
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
    
t= tabulate(tabl, tablefmt="grid")
print(t)

"""

Output:

+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
| Tx Port        | Rx Port        | Traffic Item   | Egress Tracking                               | Tx Frames   | Rx Frames   | Frames Delta | Loss % | Tx Frame Rate | Rx Frame Rate | Tx L1 Rate (bps) | Rx L1 Rate (bps) | Rx Bytes     | Tx Rate (Bps) | Rx Rate (Bps) | Tx Rate (bps) | Rx Rate (bps) | Tx Rate (Kbps) | Rx Rate (Kbps) | Tx Rate (Mbps) | Rx Rate (Mbps) | Store-Forward Avg Latency (ns) | First TimeStamp | Last TimeStamp    |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
| Ethernet - 001 | Ethernet - 002 | Traffic Item 1 | Ethernet:Outer VLAN ID (4 bits) at offset 124 | 12301807239 | 12301807217 | 22           | 0      | 13888889      | 13888889      | 10000000080      | 10000000080      | 861126505190 | 972222230     | 972222230     | 7777777840    | 7777777840    | 7777777.84     | 7777777.84     | 7777.778       | 7777.778       | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 15                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 14                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 13                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 12                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 11                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 10                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 9                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 8                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.437 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
| Ethernet - 001 | Ethernet - 002 | Traffic Item 2 | Ethernet:Outer VLAN ID (4 bits) at offset 124 | 12301807239 | 12301807217 | 22           | 0      | 13888889      | 13888889      | 10000000080      | 10000000080      | 861126505190 | 972222230     | 972222230     | 7777777840    | 7777777840    | 7777777.84     | 7777777.84     | 7777.778       | 7777.778       | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 15                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 14                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 13                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 12                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 11                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 10                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 9                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 8                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.438 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
| Ethernet - 001 | Ethernet - 002 | Traffic Item 3 | Ethernet:Outer VLAN ID (4 bits) at offset 124 | 12301807239 | 12301807217 | 22           | 0      | 13888889      | 13888889      | 10000000080      | 10000000080      | 861126505190 | 972222230     | 972222230     | 7777777840    | 7777777840    | 7777777.84     | 7777777.84     | 7777.778       | 7777.778       | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 15                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 14                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 13                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 12                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 11                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 10                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 9                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 8                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.440 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
| Ethernet - 001 | Ethernet - 002 | Traffic Item 4 | Ethernet:Outer VLAN ID (4 bits) at offset 124 | 12301807239 | 12301807217 | 22           | 0      | 13888889      | 13888889      | 10000000080      | 10000000080      | 861126505190 | 972222230     | 972222230     | 7777777840    | 7777777840    | 7777777.84     | 7777777.84     | 7777.778       | 7777.778       | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 15                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 14                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 13                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 12                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 11                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 10                                            |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 9                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
|                |                |                | 8                                             |             | 738108433   |              |        |               | 833333.5      |                  | 600000120        | 51667590310  |               | 58333345      |               | 466666760     |                | 466666.76      |                | 466.667        | 1                              | 00:00:00.657    | 2562047:47:16.441 |
+----------------+----------------+----------------+-----------------------------------------------+-------------+-------------+--------------+--------+---------------+---------------+------------------+------------------+--------------+---------------+---------------+---------------+---------------+----------------+----------------+----------------+----------------+--------------------------------+-----------------+-------------------+
"""

