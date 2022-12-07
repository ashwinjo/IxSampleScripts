from ixnetwork_restpy import SessionAssistant
from typing import List

class TestL1Settings(object):
    
    def __init__(self, ipaddr, user, password, session_id, clear_config):
        """_summary_

        Args:
            ipaddr (_type_): _description_
            user (_type_): _description_
            password (_type_): _description_
            session_id (_type_): _description_
            clear_config (_type_): _description_
        """
        session_assistant = SessionAssistant(IpAddress=ipaddr, UserName=user, Password=password,
                            LogLevel=SessionAssistant.LOGLEVEL_INFO, 
                            ClearConfig=clear_config,
                            SessionId=session_id)
        
        self.ixnetwork = session_assistant.Ixnetwork

    def vport_link_up_down(self, vports: List, operation: str):
        """_summary_

        Args:
            vports (List): _description_
            operation (str): _description_

        Returns:
            _type_: _description_
        """
        res = ""
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name = vport_name) 
            vport.LinkUpDn(Arg2=operation)
            res =  res + f"{vport_name} turned {operation}\n" 
        return res
            
        
    def vport_laser_on_off(self, vports: List, operation: str):
        """_summary_

        Args:
            vports (List): _description_
            operation (str): _description_

        Returns:
            _type_: _description_
        """
        res = ""
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name = vport_name)
            if operation.lower() == "off":
                vport.L1Config.NovusHundredGigLan.LaserOn = False
            elif operation.lower() == "on":
                vport.L1Config.NovusHundredGigLan.LaserOn = True
            res =  res + f"{vport_name} Laser: {operation}\n" 
        return res

    def vport_insert_local_fault(self, vports: List, source_value: str, dest_value: str, send_sets_mode: str):
        """_summary_

        Args:
            vports (List): _description_
            source_fault (str): _description_
            dest_fault (str): _description_
            
        """
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name = vport_name)
            vp = vport.L1Config.find().NovusHundredGigLan.find()
            
            # localFault | remoteFault
            vp.TypeAOrderedSets = source_value
            vp.TypeBOrderedSets = dest_value
            
            # alternate | typeAOnly | typeBOnly
            vp.SendSetsMode = send_sets_mode
            
            vp.StartErrorInsertion = True
            
        
    def vport_increment_decrement_frequency(self, vports: List, operation: str, step123: int):
        """_summary_

        Args:
            vports (List): _description_
            operation (str): _description_
            step123 (int): _description_
        """
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name = vport_name)
            
            vport.L1Config.find().NovusHundredGigLan.find().EnablePPM = True
            print(f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")
            
            print(vport.L1Config.NovusHundredGigLan.Ppm)
            if operation == "increment":
                vport.L1Config.find().NovusHundredGigLan.find().Ppm = step123
                print (f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")

            elif operation == "decrement":
                vport.L1Config.find().NovusHundredGigLan.find().Ppm = f"-{step123}"
                print (f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")
                
            vport.L1Config.find().NovusHundredGigLan.find().EnablePPM
            import time; time.sleep(10)
            print(f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")

    def vport_clock_source_faults(self, vports: List, loopback_mode: str):
        """_summary_

        Args:
            vports (List): _description_
            loopback_mode (str): none | lineLoopback | internalLoopback)
        """
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name = vport_name)
            print(f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")
            vport.L1Config.find().NovusHundredGigLan.find().LoopbackMode = "loopback_mode"
            print(f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")
            
    def vport_send_undersize_packets():
        """
    # Note: A Traffic Item could have multiple EndpointSets (Flow groups).
    #       Therefore, ConfigElement is a list.
    ixNetwork.info('Configuring config elements')
    configElement = trafficItem.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=50)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem.Tracking.find()[0].TrackBy = ['flowGroup0']
    
    trafficItem.Generate()
    ixNetwork.Traffic.Apply()
    ixNetwork.Traffic.StartStatelessTrafficBlocking()

    flowStatistics = session.StatViewAssistant('Flow Statistics')"""
        pass

    def vport_send_runt_packets():
        pass
    
    def vport_send_crc_packets():
        pass
            

if __name__ == "__main__":
    tl1s = TestL1Settings(ipaddr='10.36.236.121', user='admin', password='XXXXXX', session_id='12', clear_config = False)
    
    # print (tl1s.vport_laser_on_off(vports=['Port_1'], operation="on"))
    
    # print (tl1s.vport_link_up_down(vports=['Port_1'], operation="down"))
    # print (tl1s.vport_link_up_down(vports=['Port_2'], operation="down"))
    
    # print (tl1s.vport_link_up_down(vports=['Port_1'], operation="up"))
    # print (tl1s.vport_link_up_down(vports=['Port_2'], operation="up"))
    
    
    # tl1s.vport_increment_decrement_frequency(vports=['Port_1'], operation="increment", step123=70)
    # tl1s.vport_clock_source_faults(vports=['Port_1','Port_2'], loopback_mode='lineLoopback')
    
    tl1s.vport_insert_local_fault(vports=['Port_1'], source_value='localFault',dest_value='remoteFault',send_sets_mode="typeAOnly")