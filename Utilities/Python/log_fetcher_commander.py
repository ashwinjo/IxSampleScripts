
from IxOSRest import start_chassis_rest_data_fetch
from IxOSSHFetch import get_linux_chassis_information_from_cli


def start_chassis_data_fetch(CHASSIS_LIST):
    for chassis in CHASSIS_LIST:
        print(f"\n>>>>>>>>>>>>>>>>>>>>>Fetchinf informxation for Chassis{chassis['ip']}***********************\n")
        start_chassis_rest_data_fetch(chassis["ip"], chassis["username"], chassis["password"])
        if chassis["os"] == "linux" and chassis["fetch"] == "ssh":
            get_linux_chassis_information_from_cli(chassis["ip"], chassis["username"], chassis["password"])



CHASSIS_LIST = [
{
    "ip": "10.36.236.121",
    "username": "admin",
    "password": "Kimchi123Kimchi123!",
    "os": "linux",
    "fetch": ""
},
# {
#     "ip": "10.36.77.102",
#     "username": "root",
#     "password": "wrinkle#B52",
#     "os": "windows",
#     "fetch": ""
# }
                ]

start_chassis_data_fetch(CHASSIS_LIST)


"""Sample Output RestPy

ashwjosh@C0HD4NKHCX IxOS % /usr/local/bin/python3 /Users/ashwjosh/IxiaProjects/IxOS/Utilities/Python/log_fetcher_commander.py

>>>>>>>>>>>>>>>>>>>>>Fetchinf informxation for Chassis10.36.236.121***********************

getting api key ...

******************* Chassis Information ***********************

+--------------+-----------------------+-------------+-----------------------+--------------------------+----------------+-------------------------+---------+
| IxOS         | IxNetwork Protocols   | IxOS REST   | chassisSerielNumber   |   controllerSerialNumber | type           |   numberOfPhysicalCards | state   |
+==============+=======================+=============+=======================+==========================+================+=========================+=========+
| 9.30.3001.12 | 9.30.2212.1           | 1.8.1.10    | XGS12-S0250241        |                   096061 | Ixia XGS12-HSL |                       5 | UP      |
+--------------+-----------------------+-------------+-----------------------+--------------------------+----------------+-------------------------+---------+

******************* Chassis Card Information ***********************

+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
|   serialNumber |   numberOfPorts | displayName   | type                           |   parentId | revision   | MFGdatecode   |   id | state   | assemblyNumber   |   Card Number |
+================+=================+===============+================================+============+============+===============+======+=========+==================+===============+
|         539463 |              16 | N/A           | NOVUS10/1GE16DP                |       1000 | D          | P70200238     | 1101 | UP      | 850-1410-05-02   |             2 |
+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
|         541367 |               8 | N/A           | CS100GE2Q28NG+10G+25G+40G      |       1000 | E          | P73100467     | 1118 | UP      | 850-1422-03-03   |             3 |
+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
|         542248 |              40 | N/A           | NOVUS100GE8Q28+FAN+10G+25G+40G |       1000 | B          | J82810089     | 1127 | UP      | 850-1410-06-01   |             4 |
+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
|         539620 |               8 | N/A           | PerfectStorm 10GE8NG           |       1000 | D          | P70200176     | 1168 | UP      | 850-1309-02-03   |             5 |
+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
|         535153 |               4 | N/A           | XM100GE4QSFP28+ENH             |       1000 | C          | P52200279     | 1177 | UP      | 850-1318-01-01   |             6 |
+----------------+-----------------+---------------+--------------------------------+------------+------------+---------------+------+---------+------------------+---------------+
******************* Ports details ***********************
                                     owner  transceiverModel  captureState ownedState simulatedCableState  ... transmitState  transceiverSerialNumber    id cardNumber phyMode
0                                                AFBR-709SMZ         False                   NotSimulated  ...         False              AA15173PJJX  1169          5     NaN
1                                                AFBR-709DMZ         False                   NotSimulated  ...         False              AA16433068U  1170          5     NaN
2                                                ABCU-5730GZ         False                   NotSimulated  ...         False             AGC130951017  1171          5     NaN
3                                                ABCU-5740RZ         False                   NotSimulated  ...         False             AGC1528550Q7  1172          5     NaN
4                                                AFBR-709SMZ         False                   NotSimulated  ...         False              AD1505301V1  1173          5     NaN
5                                                AFBR-709DMZ         False                   NotSimulated  ...         False              AD1422300SX  1174          5     NaN
6                                                        N/A         False                   NotSimulated  ...         False                      N/A  1175          5     NaN
7                                                        N/A         False                   NotSimulated  ...         False                      N/A  1176          5     NaN
8                                                        N/A         False                   NotSimulated  ...         False                      N/A  1178          6  COPPER
9                                                        N/A         False                   NotSimulated  ...         False                      N/A  1179          6  COPPER
10                                                       N/A         False                   NotSimulated  ...         False                      N/A  1180          6  COPPER
11                                                       N/A         False                   NotSimulated  ...         False                      N/A  1181          6  COPPER
12                                                       N/A         False                   NotSimulated  ...         False                      N/A  1102          2  COPPER
13                                                       N/A         False                   NotSimulated  ...         False                      N/A  1103          2   FIBER
14                                                       N/A         False                   NotSimulated  ...         False                      N/A  1104          2   FIBER
15                                                       N/A         False                   NotSimulated  ...         False                      N/A  1105          2   FIBER
16                                             FTLX8571D3BCL         False                   NotSimulated  ...         False                  AMJ00BP  1106          2   FIBER
17                                                       N/A         False                   NotSimulated  ...         False                      N/A  1107          2   FIBER
18                                             FTLX8571D3BCL         False                   NotSimulated  ...         False                  MVC1M6M  1108          2   FIBER
19                                               AFBR-709SMZ         False                   NotSimulated  ...         False              AD1620303EC  1109          2   FIBER
20                                                       N/A         False                   NotSimulated  ...         False                      N/A  1110          2   FIBER
21                                                       N/A         False                   NotSimulated  ...         False                      N/A  1111          2   FIBER
22                                                       N/A         False                   NotSimulated  ...         False                      N/A  1112          2   FIBER
23                                                       N/A         False                   NotSimulated  ...         False                      N/A  1113          2   FIBER
24                                          FTLX8571D3BCL-N2         False                   NotSimulated  ...         False            FNSRMYAPD1V1X  1114          2   FIBER
25                                                       N/A         False                   NotSimulated  ...         False                      N/A  1115          2   FIBER
26                                             FTLX8574D3BCL         False                   NotSimulated  ...         False                  A19BN3Z  1116          2   FIBER
27                                             FTLX8574D3BCL         False                   NotSimulated  ...         False                  A1AB0TQ  1117          2   FIBER
28                   BreakingPoint/admin/1     FCBN425QB1C03         False                   NotSimulated  ...         False                  DTS01WE  1119          3  COPPER
29                   BreakingPoint/admin/1     FCBN425QB1C03         False                   NotSimulated  ...         False                  DTS01WE  1120          3  COPPER
30                                             MMA1B00-C100D         False                   NotSimulated  ...         False            MT1710FT00519  1128          4  COPPER
31                                             MMA1B00-C100D         False                   NotSimulated  ...         False            MT1646FT00232  1129          4  COPPER
32                                               AFBR-79EIDZ         False                   NotSimulated  ...         False                 QE109424  1130          4  COPPER
33                                                       N/A         False                   NotSimulated  ...         False                      N/A  1131          4  COPPER
34                                                       N/A         False                   NotSimulated  ...         False                      N/A  1132          4  COPPER
35                                               AFBR-79EIDZ         False                   NotSimulated  ...         False                 QF42013S  1133          4  COPPER
36                                              MFA1A00-C003         False                   NotSimulated  ...         False            MT1836FT02919  1134          4  COPPER
37  IxNetwork/WIN-0TITARHGJ7D/ashwin.73844      MFA1A00-C003         False                   NotSimulated  ...         False            MT1836FT02919  1135          4  COPPER

[38 rows x 20 columns]
******************* Ports ownership details ***********************
                                    owner transceiverModel  captureState ownedState simulatedCableState  ... transmitState  transceiverSerialNumber    id phyMode cardNumber
0                   BreakingPoint/admin/1    FCBN425QB1C03         False                   NotSimulated  ...         False                  DTS01WE  1119  COPPER          3
1                   BreakingPoint/admin/1    FCBN425QB1C03         False                   NotSimulated  ...         False                  DTS01WE  1120  COPPER          3
2  IxNetwork/WIN-0TITARHGJ7D/ashwin.73844     MFA1A00-C003         False                   NotSimulated  ...         False            MT1836FT02919  1135  COPPER          4

[3 rows x 20 columns]

******************* Percentage ports having owners ***********************

% ports owned total 7.894736842105263
% ports free total 92.10526315789474

******************* Users on Chassis ***********************

ashwin.73844:--1
1:--2
Polling for async operation ...
SUCCESS
Completed async operation
https://10.36.236.121/platform/api/v2/licensing/servers/1/operations/retrievelicenses/48/result
        activationCode  quantity                                        description   expiryDate
0  0457-8298-A66F-55D7         1        IXIA IxLoad Multiplay-2016, Software Bundle  25-Jul-2023
1  4A20-2AE6-93F9-2045         1  IXIA IxNetwork, Optional Software, Bonded GRE ...  26-Jan-2023
2  5544-5624-143A-7D3D         1  IXIA FRAMEWORK (IxServer), IXOS SOFTWARE, NODE...  05-Jul-2023
3  7292-5B0F-0CA3-FB4B         1     IXIA IxNetwork, Bundle Software Package Tier 3  17-Jul-2023
4  765C-E1A8-2CDA-21E1         1  IXIA IxNetwork, All Inclusive package for 2-Sl...  17-Jul-2023
5  DC65-7B8F-B263-E176         1  IXIA IxNetwork, All Inclusive package for Chassis  17-Jul-2023
6  DD73-2BED-0A34-F922         1  IXIA IxNetwork, All Inclusive package for Chassis  17-Jul-2023
7  FA54-8BDE-3F8A-62DF         1       IXIA IxNetwork Protocol Emulation over EoGRE  26-Jan-2023

******************* Chassis Performance Metrics ***********************

   memoryInUseBytes  memoryTotalBytes  diskIOBytesPerSecond  cpuUsagePercent
0       11801092096       67417124864                   0.0          1.75769
    bytesReceived            lastUpdatedUTC  framesSent  fragments   bytesSent    id  validFramesReceived  alignmentErrors  parentId  crcErrors
0               0  2023-02-14T12:29:23.252Z           0          0           0  1600                    0                0      1117          0
1               0  2023-02-14T12:29:23.252Z           0          0           0  1601                    0                0      1116          0
2               0  2023-02-14T12:29:23.252Z           0          0           0  1602                    0                0      1115          0
3               0  2023-02-14T12:29:23.252Z           0          0           0  1603                    0                0      1114          0
4               0  2023-02-14T12:29:23.252Z           0          0           0  1604                    0                0      1113          0
5               0  2023-02-14T12:29:23.252Z           0          0           0  1605                    0                0      1112          0
6               0  2023-02-14T12:29:23.252Z           0          0           0  1606                    0                0      1111          0
7               0  2023-02-14T12:29:23.252Z           0          0           0  1607                    0                0      1110          0
8               0  2023-02-14T12:29:23.252Z           0          0           0  1608                    0                0      1109          0
9               0  2023-02-14T12:29:23.252Z           0          0           0  1609                    0                0      1108          0
10              0  2023-02-14T12:29:23.252Z           0          0           0  1610                    0                0      1107          0
11              0  2023-02-14T12:29:23.252Z           0          0           0  1611                    0                0      1106          0
12              0  2023-02-14T12:29:23.252Z           0          0           0  1612                    0                0      1105          0
13              0  2023-02-14T12:29:23.252Z           0          0           0  1613                    0                0      1104          0
14              0  2023-02-14T12:29:23.252Z           0          0           0  1614                    0                0      1103          0
15              0  2023-02-14T12:29:23.252Z           0          0           0  1615                    0                0      1102          0
16     1360485217  2023-02-14T12:29:23.252Z     7634471          0  8356098187  1616              7681975                0      1120          0
17     8356098187  2023-02-14T12:29:23.252Z     7681975          0  1360485217  1617              7634471                0      1119          0
18              0  2023-02-14T12:29:23.252Z           0          0           0  1618                    0                0      1135          0
19              0  2023-02-14T12:29:23.252Z           0          0           0  1619                    0                0      1134          0
20              0  2023-02-14T12:29:23.252Z           0          0           0  1620                    0                0      1133          0
21              0  2023-02-14T12:29:23.252Z           0          0           0  1621                    0                0      1132          0
22              0  2023-02-14T12:29:23.252Z           0          0           0  1622                    0                0      1131          0
23              0  2023-02-14T12:29:23.252Z           0          0           0  1623                    0                0      1130          0
24              0  2023-02-14T12:29:23.252Z           0          0           0  1624                    0                0      1129          0
25              0  2023-02-14T12:29:23.252Z           0          0           0  1625                    0                0      1128          0
26              0  2023-02-14T12:29:23.252Z           0          0           0  1626                    0                0      1176          0
27            390  2023-02-14T12:29:23.252Z           0         15           0  1627                    0                0      1175          1
28              0  2023-02-14T12:29:23.252Z           0          0           0  1628                    0                0      1174          0
29              0  2023-02-14T12:29:23.252Z           0          0           0  1629                    0                0      1173          0
30              0  2023-02-14T12:29:23.252Z           0          0           0  1630                    0                0      1172          0
31              0  2023-02-14T12:29:23.252Z           0          0           0  1631                    0                0      1171          0
32              0  2023-02-14T12:29:23.252Z           0          0           0  1632                    0                0      1170          0
33              0  2023-02-14T12:29:23.252Z           0          0           0  1633                    0                0      1169          0
34              0  2023-02-14T12:29:23.252Z           0          0           0  1634                    0                0      1181          0
35              0  2023-02-14T12:29:23.252Z           0          0           0  1635                    0                0      1180          0
36              0  2023-02-14T12:29:23.252Z           0          0           0  1636                    0                0      1179          0
37              0  2023-02-14T12:29:23.252Z           0          0           0  1637                    0                0      1178          0

    
"""