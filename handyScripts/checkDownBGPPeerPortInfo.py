# Import the RestPy module
from ixnetwork_restpy import SessionAssistant
#from ixnetwork_restpy import *

import pprint



def check_for_down_sessions(session, vport_map):

    down_bgp_peer_session_topo_port_info = []
    topos = session.Ixnetwork \
    .Topology.find() \
    
    for topo in topos: 
        value_dict = {}
        port_connected_to = []
        topo_name = topo.Name
        value_dict.update({"TopologyName": topo_name})
        for vport in topo.Vports:
            internal_id = vport.split('/')[-1]
            # print(f"Vport {vport} is connected to {vport_map.get(int(internal_id))}")
            port_connected_to.append(vport_map.get(int(internal_id))) 
                
        value_dict.update({"PortsTopoConnectedTo": port_connected_to})
        dgs = topo.DeviceGroup.find() \
        
        for dg in dgs:
            bgpipv4peer = dg.Ethernet.find() \
            .Ipv4.find() \
            .BgpIpv4Peer.find()
            dg_name = dg.Name
            
            value_dict.update({"DeviceGroupName": dg_name})
            for a in bgpipv4peer:
                peer_status_map = {}
                bgpipv4peer_name = a.Name
            
                
                for ip, status in zip(a.LocalIpv4Ver2, a.SessionStatus):
                    if status.lower() == 'down':
                        peer_status_map.update({ip:status})
            value_dict.update({"BgpIpv4PeerName": bgpipv4peer_name})
            value_dict.update({"bgpDownPeerInfo": peer_status_map})
        down_bgp_peer_session_topo_port_info.append(value_dict)
    return down_bgp_peer_session_topo_port_info
            
            
def get_vport_map(session):
    vports = session.Ixnetwork \
	.Vport.find()
    vport_map = {}
    for vp in vports:
        vport_map.update({vp.InternalId: vp.AssignedToDisplayName})
    return vport_map



def main():
    apiServerIp = 'X.X.X.X'
    # For Linux API server only
    username = 'admin'
    password = 'XXXXXXXXXXXXXXXX'
    session = SessionAssistant(IpAddress=apiServerIp, RestPort=None, UserName=username, Password=password, 
                                SessionName=None, SessionId=31, ApiKey=None,
                                ClearConfig=False, LogLevel='info', LogFilename='restpy.log')


    vport_map = get_vport_map(session)
    down_bgp_peer_session_topo_port_info = check_for_down_sessions(session, vport_map)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(down_bgp_peer_session_topo_port_info)
    
if __name__ == "__main__":
    main()


""" Sample Output:

base) ashwjosh@C0HD4NKHCX IxNetworkAutomationDemo % /usr/local/bin/python3 /Users/ashwjosh/IxNetworkAutomationDemo/check_down_bgp_peers.py
2023-06-21 19:57:28 [ixnetwork_restpy.connection tid:8269929984] [INFO] using python version 3.11.0 (v3.11.0:deaf509e8f, Oct 24 2022, 14:43:23) [Clang 13.0.0 (clang-1300.0.29.30)]
2023-06-21 19:57:28 [ixnetwork_restpy.connection tid:8269929984] [INFO] using ixnetwork-restpy version 1.1.7
2023-06-21 19:57:28 [ixnetwork_restpy.connection tid:8269929984] [WARNING] Verification of certificates is disabled
2023-06-21 19:57:28 [ixnetwork_restpy.connection tid:8269929984] [INFO] Determining the platform and rest_port using the X.X.X.X address...
2023-06-21 19:57:28 [ixnetwork_restpy.connection tid:8269929984] [WARNING] Unable to connect to http://X.X.X.X:443.
2023-06-21 19:57:29 [ixnetwork_restpy.connection tid:8269929984] [INFO] Connection established to `https://X.X.X.X:443 on linux`
2023-06-21 19:57:29 [ixnetwork_restpy.connection tid:8269929984] [INFO] Using IxNetwork api server version 9.30.2212.7
2023-06-21 19:57:29 [ixnetwork_restpy.connection tid:8269929984] [INFO] User info IxNetwork/ixnetworkweb/admin-31-22924
[   {   'BgpIpv4PeerName': 'BGP Peer 1',
        'DeviceGroupName': 'Device Group 2',
        'PortsTopoConnectedTo': [   '10.36.236.121;04;07',
                                    '10.36.236.121;02;15',
                                    '10.36.236.121;02;16'],
        'TopologyName': 'Topology 1',
        'bgpDownPeerInfo': {   '20.1.1.1': 'down',
                               '20.1.10.1': 'down',
                               '20.1.11.1': 'down',
                               '20.1.12.1': 'down',
                               '20.1.13.1': 'down',
                               '20.1.14.1': 'down',
                               '20.1.15.1': 'down',
                               '20.1.2.1': 'down',
                               '20.1.3.1': 'down',
                               '20.1.4.1': 'down',
                               '20.1.5.1': 'down',
                               '20.1.6.1': 'down',
                               '20.1.7.1': 'down',
                               '20.1.8.1': 'down',
                               '20.1.9.1': 'down'}},
    {   'BgpIpv4PeerName': 'BGP Peer 2',
        'DeviceGroupName': 'Device Group 4',
        'PortsTopoConnectedTo': ['10.36.236.121;04;08'],
        'TopologyName': 'Topology 3',
        'bgpDownPeerInfo': {   '20.1.1.2': 'down',
                               '20.1.2.2': 'down',
                               '20.1.3.2': 'down',
                               '20.1.4.2': 'down',
                               '20.1.5.2': 'down'}}]



""""
