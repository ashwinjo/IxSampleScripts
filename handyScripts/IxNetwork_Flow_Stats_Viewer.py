from ixnetwork_restpy import SessionAssistant
from typing import List



session_assistant = SessionAssistant(IpAddress="10.36.236.121", UserName="admin", Password="XXXXXXX!",
                            LogLevel=SessionAssistant.LOGLEVEL_INFO, 
                            ClearConfig=False,
                            SessionId=1)


ixnetwork = session_assistant.Ixnetwork

flowStatistics = session_assistant.StatViewAssistant('Flow Statistics')


print ('Tx Port', 'Rx Port', 'Loss %', 'IPv4 :Default PHB')
for rowNumber,flowStat in enumerate(flowStatistics.Rows):
    print (flowStat['Tx Port'], flowStat['Rx Port'], flowStat['Loss %'], flowStat['IPv4 :Default PHB'])

"""
====== Output =======

(base) ashwjosh@C0HD4NKHCX IxNetworkAutomationDemo % /usr/local/bin/python3 /Users/ashwjosh/IxNetworkAutomationDemo/mixed_fiber_type.py
2023-07-28 01:17:35 [ixnetwork_restpy.connection tid:8195005952] [INFO] using python version 3.11.0 (v3.11.0:deaf509e8f, Oct 24 2022, 14:43:23) [Clang 13.0.0 (clang-1300.0.29.30)]
2023-07-28 01:17:35 [ixnetwork_restpy.connection tid:8195005952] [INFO] using ixnetwork-restpy version 1.1.10
2023-07-28 01:17:35 [ixnetwork_restpy.connection tid:8195005952] [WARNING] Verification of certificates is disabled
2023-07-28 01:17:35 [ixnetwork_restpy.connection tid:8195005952] [INFO] Determining the platform and rest_port using the 10.36.236.121 address...
2023-07-28 01:17:37 [ixnetwork_restpy.connection tid:8195005952] [WARNING] Unable to connect to http://10.36.236.121:11009.
2023-07-28 01:17:39 [ixnetwork_restpy.connection tid:8195005952] [WARNING] Unable to connect to https://10.36.236.121:11009.
2023-07-28 01:17:39 [ixnetwork_restpy.connection tid:8195005952] [WARNING] Unable to connect to http://10.36.236.121:443.
2023-07-28 01:17:40 [ixnetwork_restpy.connection tid:8195005952] [INFO] Connection established to `https://10.36.236.121:443 on linux`
2023-07-28 01:17:40 [ixnetwork_restpy.connection tid:8195005952] [INFO] Using IxNetwork api server version 9.30.2212.7
2023-07-28 01:17:40 [ixnetwork_restpy.connection tid:8195005952] [INFO] User info IxNetwork/ixnetworkweb/admin-1-6748
Tx Port Rx Port Loss % IPv4 :Default PHB
Ethernet - 001 Ethernet - 002 0.000 0
Ethernet - 001 Ethernet - 002 0.000 10
Ethernet - 001 Ethernet - 002 0.000 20
Ethernet - 001 Ethernet - 002 0.000 32
Ethernet - 001 Ethernet - 002 0.000 46

=======================

flowStatus object View:

Row:3  View:Flow Statistics  Sampled:2023-07-28 01:15:31.187498 UTC
        Tx Port: Ethernet - 001
        Rx Port: Ethernet - 002
        Traffic Item: Traffic Item 1
        IPv4 :Default PHB: 32
        Tx Frames: 30776
        Rx Frames: 30776
        Frames Delta: 0
        Loss %: 0.000
        Tx Frame Rate: 39.000
        Rx Frame Rate: 39.000
        Tx L1 Rate (bps): 46176.000
        Rx L1 Rate (bps): 46176.000
        Rx Bytes: 3939328
        Tx Rate (Bps): 4992.000
        Rx Rate (Bps): 4992.000
        Tx Rate (bps): 39936.000

"""
