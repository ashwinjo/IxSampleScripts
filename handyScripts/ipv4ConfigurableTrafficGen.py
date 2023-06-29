from ixnetwork_restpy import SessionAssistant
import json

import time


def getIxiaConfiguration():
    with open("testCaseTgenConfig.json", "r+") as f:
        config = json.loads(f.read())
    return config

config = getIxiaConfiguration()['tgenConfig']

class TrafficGenerator(object):
    
    def __init__(self, apiServerIp=None, apiServerUsername=None, apiServerPassword=None, 
                 newSession=True, connectToExisiting=False, sessionId=None):
        self.apiServerIp = apiServerIp
        self.apiServerUsername = apiServerUsername
        self.apiServerPassword = apiServerPassword
        self.newSession = newSession
        self.connectToExisiting = connectToExisiting
        self. sessionId = sessionId
        self.config = config
        self.session_assistant = SessionAssistant(IpAddress=self.apiServerIp, 
                                                UserName=self.apiServerUsername, 
                                                Password= self.apiServerPassword,
                                                SessionId=sessionId,
                                                LogLevel=SessionAssistant.LOGLEVEL_INFO, 
                                                ClearConfig=self.newSession)

    def _connect_ports(self):
        portMap = self.session_assistant.PortMapAssistant()
        self.vport = dict()
        for item in self.config:
            if "endpoint" in item:
                print(self.config[item]["ixia-chassis-port-name"])
                self.vport[self.config[item]["ixia-chassis-port-name"]] = portMap.Map(self.config[item]["ixia-chassis-ip"], 
                                                                                        CardId=self.config[item]["ixia-chassis-card"], 
                                                                                        PortId=self.config[item]["ixia-chassis-port"], 
                                                                                        Name=self.config[item]["ixia-chassis-port-name"])
        
        forceTakePortOwnership = True
        portMap.Connect(forceTakePortOwnership)
    
    def _create_topology(self):
        self.ipv4list = []
        self.ngpool = []
        
        for item in self.config:
            if "endpoint" in item:
                topology = self.session_assistant.Ixnetwork.Topology.add(Name=self.config[item]["topology"]["name"],
                                                                          Ports=self.vport[self.config[item]["topology"]["vport"]])
                devgrp = topology.DeviceGroup.add(Name=self.config[item]["topology"]["devicegroup"]["name"], 
                                                  Multiplier=self.config[item]["topology"]["devicegroup"]["multipier"])
                
                ethernet = devgrp.Ethernet.add(Name=self.config[item]["topology"]["devicegroup"]["ethernet"]["name"])
                ethernet.EnableVlans.Single(True)
                
                # Creating IPv4 - Layer 3

                ipv4 = ethernet.Ipv4.add(Name=self.config[item]["topology"]["devicegroup"]["ipv4"]["name"])
                ipv4.Address.Increment(start_value=self.config[item]["topology"]["devicegroup"]["ipv4"]["addressStartValue"], 
                                       step_value=self.config[item]["topology"]["devicegroup"]["ipv4"]["addressIncrement"])
                ipv4.GatewayIp.Increment(start_value=self.config[item]["topology"]["devicegroup"]["ipv4"]["gatewayStartValue"], 
                                         step_value=self.config[item]["topology"]["devicegroup"]["ipv4"]["gatewayIncrement"])
                self.ipv4list.append(ipv4)
        
        
                self.session_assistant.Ixnetwork.info('Configuring BgpIpv4Peer')
                bgp2 = ipv4.BgpIpv4Peer.add(Name=self.config[item]["topology"]["devicegroup"]["bgp"]["name"])
                bgp2.DutIp.Increment(start_value=self.config[item]["topology"]["devicegroup"]["bgp"]["increment"], 
                                     step_value=self.config[item]["topology"]["devicegroup"]["bgp"]["step_value"])
                bgp2.Type.Single('external')
                bgp2.LocalAs2Bytes.Increment(start_value=self.config[item]["topology"]["devicegroup"]["bgp"]["localas2value"], 
                                             step_value=0)

                self.session_assistant.Ixnetwork.info('Configuring Network Group 2')
                networkGroup = devgrp.NetworkGroup.add(Name=self.config[item]["topology"]["networkpools"]["name"], 
                                                        Multiplier=self.config[item]["topology"]["networkpools"]["multiplier"])
                ipv4PrefixPool = networkGroup.Ipv4PrefixPools.add(NumberOfAddresses=self.config[item]["topology"]["networkpools"]["numberOfIpv4PrefixPools"])
                
                ipv4PrefixPool.NetworkAddress.Increment(start_value=self.config[item]["topology"]["networkpools"]["start_value"], 
                                                        step_value=self.config[item]["topology"]["networkpools"]["step_value"])
                                                        
                ipv4PrefixPool.PrefixLength.Single(self.config[item]["topology"]["networkpools"]["prefix_length"])
                self.ngpool.append(ipv4PrefixPool)
            
               
    def _start_protocols(self):
        self.session_assistant.Ixnetwork.StartAllProtocols(Arg1='sync')
        # Create Protocol Sessions
        protocolSummary = self.session_assistant.StatViewAssistant('Protocols Summary')
        protocolSummary.CheckCondition('Sessions Not Started', protocolSummary.EQUAL, 0)
        protocolSummary.CheckCondition('Sessions Down', protocolSummary.EQUAL, 0)
        self.session_assistant.Ixnetwork.info(protocolSummary)
    
    def _start_traffic(self):
        self.config["traffic"]
        self.session_assistant.Ixnetwork.info('Create Traffic Item')
        for ti in self.config["traffic"]:
            trafficItem = self.session_assistant.Ixnetwork.Traffic.TrafficItem.add(Name=ti["name"], 
                                                                                BiDirectional=ti["BiDirectional"], 
                                                                                TrafficType=ti["TrafficType"])

        
            self.session_assistant.Ixnetwork.info('Add endpoint flow group')
            trafficItem.EndpointSet.add(Sources=self.ngpool[0], Destinations=self.ngpool[1])
            trafficItem.Tracking.find().TrackBy= ti["TrackingType"]
                                                   
            trafficItem.Generate()
            self.session_assistant.Ixnetwork.Traffic.Apply()
            self.session_assistant.Ixnetwork.Traffic.StartStatelessTrafficBlocking()

    def _fetch_stats(self):
        flowStatistics = self.session_assistant.StatViewAssistant('Flow Statistics')
        self.session_assistant.Ixnetwork.info(flowStatistics)
        for rowNumber,flowStat in enumerate(flowStatistics.Rows):
            self.session_assistant.Ixnetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))
            self.session_assistant.Ixnetwork.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}\n'.format(
                rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
                flowStat['Tx Frames'], flowStat['Rx Frames']))
        self.session_assistant.Ixnetwork.Traffic.StopStatelessTrafficBlocking()
       
    
 
 
 
if __name__ == "__main__":

    # get the start time
    st = time.time()
    tg = TrafficGenerator(config['apiServerIp'], apiServerUsername=config["apiServerUsername"],
                        apiServerPassword=config["apiServerPassword"], sessionId=32)
    tg._connect_ports()
    tg._create_topology()
    tg._start_protocols()
    tg._start_traffic()
    tg._fetch_stats()
    
    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
    
# Execution time for profile approcah vs 
# Run Traffic for 2 Mins
# Enable Tracking
