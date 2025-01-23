from ixnetwork_restpy import SessionAssistant
import time

final_table = []
apiServerIp = '10.36.236.121'

session = SessionAssistant(IpAddress=apiServerIp, RestPort=None, UserName='admin', Password='XXXXXXXXXX', 
                            SessionName=None, SessionId=1, ApiKey=None,
                            ClearConfig=False)


"""
Customer Requirement:

Example:
1. BGP peer of device group1 has Network Group 1 , Network Group 2 , Network Group 3 of prefixes
2. Lets say we start Device Group 1 at T1
3. Have the ability to start network Group 1 at T2
4. Have the ability to start network Group 2 at T3 and so on
"""

# I have DG1 with 3 NG assigned to it
ngs = ["networkGroup1", "Network Group 1", "Network Group 2"]
for ng in ngs:
    #disable_it before starting the DG
    session.Ixnetwork.Topology.find(Name = "Topo1").DeviceGroup.find(Name = "DG1").NetworkGroup.find(Name=ng).Enabled.Single(False)


# Start Device Groups 
session.Ixnetwork.Topology.find(Name = "Topo1").DeviceGroup.find(Name = "DG1").Start()
session.Ixnetwork.Topology.find(Name = "Topo2").DeviceGroup.find(Name = "DG2").Start()


# Ensure protocols up. You can also use StartAllProtocols, upto you

for ng in ngs:
    time.sleep(10)
    #enable_it first NG at at Tn
    session.Ixnetwork.Topology.find(Name = "Topo1").DeviceGroup.find(Name = "DG1").NetworkGroup.find(Name=ng).Enabled.Single(True)

    # Add logic may be to check for learned infor here to confirm



    
