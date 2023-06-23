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
        
        value_dict = get_ipv4_neighbors(dgs, value_dict)
        value_dict_final = get_ipv6_neighbors(dgs, value_dict)
        
        down_bgp_peer_session_topo_port_info.append(value_dict_final)
    return down_bgp_peer_session_topo_port_info


def get_ipv6_neighbors(dgs, value_dict):
    for dg in dgs:
            bgpipv6peer = dg.Ethernet.find() \
            .Ipv6.find() \
            .BgpIpv6Peer.find()
            dg_name = dg.Name
            
            value_dict.update({"DeviceGroupName": dg_name})
            for a in bgpipv6peer:
                peer_status_map = {}
                bgpipv4peer_name = a.Name
            
                
                for ip, status in zip(a.LocalIpv6Ver2, a.SessionStatus):
                    if status.lower() == 'down':
                        peer_status_map.update({ip:status})
            value_dict.update({"BgpIpv6PeerName": bgpipv4peer_name})
            value_dict.update({"bgpv6DownPeerInfo": peer_status_map})
    return value_dict

def get_ipv4_neighbors(dgs, value_dict):
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
            value_dict.update({"bgpv4DownPeerInfo": peer_status_map})
    return value_dict
            
            
def get_vport_map(session):
    vports = session.Ixnetwork \
	.Vport.find()
    vport_map = {}
    for vp in vports:
        vport_map.update({vp.InternalId: vp.AssignedToDisplayName})
    return vport_map



def main():
    apiServerIp = '10.36.236.121'
    # For Linux API server only
    username = 'admin'
    password = 'XXXXXXXXX'
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

(base) ashwjosh@C0HD4NKHCX IxNetworkAutomationDemo % /usr/local/bin/python3 /Users/ashwjosh/IxNetworkAutomationDemo/check_down_bgp_peers.py
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [INFO] using python version 3.11.0 (v3.11.0:deaf509e8f, Oct 24 2022, 14:43:23) [Clang 13.0.0 (clang-1300.0.29.30)]
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [INFO] using ixnetwork-restpy version 1.1.7
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [WARNING] Verification of certificates is disabled
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [INFO] Determining the platform and rest_port using the 10.36.236.121 address...
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [WARNING] Unable to connect to http://10.36.236.121:443.
2023-06-23 19:33:57 [ixnetwork_restpy.connection tid:8269929984] [INFO] Connection established to `https://10.36.236.121:443 on linux`
2023-06-23 19:33:58 [ixnetwork_restpy.connection tid:8269929984] [INFO] Using IxNetwork api server version 9.30.2212.7
2023-06-23 19:33:58 [ixnetwork_restpy.connection tid:8269929984] [INFO] User info IxNetwork/ixnetworkweb/admin-31-22924

[{
		'BgpIpv4PeerName': 'bgp_1',
		'BgpIpv6PeerName': 'BGP+ Peer 3',
		'DeviceGroupName': 'DG1',
		'PortsTopoConnectedTo': ['10.36.236.121;04;07'],
		'TopologyName': 'Topo1',
		'bgpv4DownPeerInfo': {
			'1.1.1.1': 'down',
			'1.1.1.2': 'down'
		},
		'bgpv6DownPeerInfo': {
			'2000:0:2:1:0:0:0:2': 'down',
			'2000:0:2:2:0:0:0:2': 'down'
		}
	},
	{
		'BgpIpv4PeerName': 'bgp_2',
		'BgpIpv6PeerName': 'BGP+ Peer 1',
		'DeviceGroupName': 'DG2',
		'PortsTopoConnectedTo': ['10.36.236.121;04;08'],
		'TopologyName': 'Topo2',
		'bgpv4DownPeerInfo': {
			'1.1.1.3': 'down',
			'1.1.1.4': 'down'
		},
		'bgpv6DownPeerInfo': {
			'2000:0:1:1:0:0:0:2': 'down',
			'2000:0:1:2:0:0:0:2': 'down'
		}
	}
]
""""
