from ixnetwork_restpy.testplatform.testplatform import TestPlatform # ixnetwork_restpy==1.0.45
import time
from typing import List

traffic_item_name = "Topo1 to Topo2"

class TestL1Settings(object):

    def __init__(self, ipaddr, user, password, session_name=None, session_id=None):
        """Constructor for TestCase CLasses
        Args:
            ipaddr (_type_): ip of ixia chasses
            user (_type_): username for ixia chassis
            password (_type_): password for ixia chassis
            session_name (_type_): session name on Ixia Linux chassis to connect to
        """
        testPlatform = TestPlatform(ip_address=ipaddr, log_file_name='restpy.log')
        testPlatform.Trace = 'request_response'
        testPlatform.Authenticate(user, password)
        
        # Multiple sessions possible only with Linux Chassis
        if not session_name:
            session_assistant = testPlatform.Sessions.find()
        elif session_id:
            session_assistant = testPlatform.Sessions.find(Id=session_id)
        elif session_name:
            session_assistant = testPlatform.Sessions.find(Name=session_name)
        self.ixnetwork = session_assistant.Ixnetwork
    

    def vport_link_up_down(self, **kwargs):
        """Turn L1 Ports UP/Down
        Returns:
            _type_: _description_
        """
        res = ""
        vports = kwargs.get("vports")
        operation =  kwargs.get("operation")
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            
            vport.LinkUpDn(Arg2=operation)
            res = res + f"{vport_name} turned {operation}\n"
        print(res)

    def vport_laser_on_off(self, **kwargs):
        """Turn Laser On Off
        Returns:ß
            _type_: _description_
        """
        res = ""
        vports = kwargs.get("vports")
        operation =  kwargs.get("operation")
        print(vports, operation)
        
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            if operation.lower() == "off":
                vport.L1Config.NovusHundredGigLan.LaserOn = False
            elif operation.lower() == "on":
                vport.L1Config.NovusHundredGigLan.LaserOn = True
            res = res + f"{vport_name} Laser: {operation}\n"
        print(res)

    def vport_insert_local_fault(self, **kwargs):
        """Insert L1 local/remote fauls and then initiate their transmission
        """
        vports = kwargs.get("vports")
        source_value =  kwargs.get("source_value")
        dest_value = kwargs.get("dest_value")
        send_sets_mode =  kwargs.get("send_sets_mode")
        
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            vp = vport.L1Config.NovusHundredGigLan

            # localFault | remoteFault
            vp.TypeAOrderedSets = source_value
            vp.TypeBOrderedSets = dest_value

            # alternate | typeAOnly | typeBOnly
            vp.SendSetsMode = send_sets_mode

            vp.StartErrorInsertion = True
            print(vp)
            

    def vport_increment_decrement_frequency(self, vports: List, operation: str, step_size: int):
        """Increment Decrement Transmit deviation
        Args:
            vports (List): Ports to apply changes on
            operation (str): increment/decrement frequency
            step_size (int): incement/decrement by what value
        """
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)

            vport.L1Config.NovusHundredGigLan.EnablePPM = True
            print(
                f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")

            print(vport.L1Config.NovusHundredGigLan.Ppm)
            if operation == "increment":
                vport.L1Config.NovusHundredGigLan.Ppm = step_size
                print(f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")

            elif operation == "decrement":
                vport.L1Config.NovusHundredGigLan.Ppm = f"-{step_size}"
                print(f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")

            vport.L1Config.NovusHundredGigLan.EnablePPM
            time.sleep(5)
            print(
                f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")

    def vport_clock_source_faults(self, **kwargs):
        """Inserting clock faults bases on loopback modes
        """
        vports = kwargs.get("vports")
        loopback_mode =  kwargs.get("loopback_mode")
        
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            print(
                f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")
            vport.L1Config.NovusHundredGigLan.LoopbackMode = loopback_mode
            print(
                f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")

    def vport_send_undersize_packets(self, **kwargs):
        """Sending frames with modified attributes for frame size, crc
        """
        create_traffic_item = kwargs.get("create_traffic_item", False)
        traffic_item_name = kwargs.get("traffic_item_name", "TI")
        undersize = kwargs.get("undersize", False)
        runt = kwargs.get("runt", False)
        crc = kwargs.get("crc", False)
        desired_frame_size = kwargs.get("desired_frame_size", "128")
        
        # get topology objects

        topology1 = self.ixnetwork.Topology.find()[0]
        topology2 = self.ixnetwork.Topology.find()[1]

        if create_traffic_item:
            trafficItem = self.ixnetwork.Traffic.TrafficItem.add(
                Name='TI', BiDirectional=False, TrafficType='ipv4')
            trafficItem.EndpointSet.add(
                Sources=topology1, Destinations=topology2)
            self.ixnetwork.info('Configuring config elements')
            configElement = trafficItem.ConfigElement.find()[0]
            configElement.FrameRate.update(Type='percentLineRate', Rate=50)
            configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
            configElement.FrameSize.FixedSize = 128
            trafficItem.Tracking.find()[0].TrackBy = ['flowGroup0']
            trafficItem.Generate()
        else:
            # Get the config element
            configElement = self.ixnetwork.Traffic.TrafficItem.find(
                Name=traffic_item_name).ConfigElement.find()[0]
            if undersize:
                configElement.FrameSize.FixedSize = desired_frame_size

            if runt or crc:
                configElement.FrameSize.FixedSize = desired_frame_size
                configElement.Crc = 'goodCrc'
                
                print(configElement)


if __name__ == "__main__":
    
    # No need to pass session_name when testing on Windows Ixia Chassis
    tl1s = TestL1Settings(ipaddr='ixiaapiserverip', user='admin',
                          password='somepassword!', session_name="testbed_ashwjosh")

       
    def link_up_down(vports, wait_interval, repetition):
        
        for _ in range(repetition):
            tl1s.vport_link_up_down(vports=vports, operation="down")
            time.sleep(wait_interval)
            tl1s.vport_link_up_down(vports=vports, operation="up")
            
            
    def laser_on_off(vports, wait_interval, repetition):
        
        for _ in range(repetition):
            tl1s.vport_link_up_down(vports=vports, operation="down")
            time.sleep(wait_interval)
            tl1s.vport_link_up_down(vports=vports,  operation="up")

    def vport_clock_source_faults_toggle(vports, wait_interval, repetition, toggle_states=["none", "lineLoopback", "internalLoopback"]):
        for _ in range(repetition):
            for state in toggle_states:
                tl1s.vport_clock_source_faults(vports=vports, loopback_mode=state)
                time.sleep(wait_interval)
            
            
    def generate_faults(vports, wait_interval, repetition):
        for _ in range(repetition):
            tl1s.vport_insert_local_fault(vports=vports, source_value='localFault',dest_value='remoteFault',send_sets_mode="typeAOnly")
            time.sleep(wait_interval)
            tl1s.vport_insert_local_fault(vports=vports, source_value='localFault',dest_value='remoteFault',send_sets_mode="typeBOnly")
        
    def generate_crc_error_traffic(traffic_item_name, wait_interval, repetition):
        for _ in range(repetition):
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, crc=True, desired_frame_size=128)
            time.sleep(wait_interval)
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, crc=False, desired_frame_size=128)
    
    def generate_undersize_packets_traffic(traffic_item_name, wait_interval, repetition):
        for _ in range(repetition):
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, undersize=True, desired_frame_size=60)
            time.sleep(wait_interval)
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, undersize=False, desired_frame_size=60)
    
    def generate_runt_traffic(traffic_item_name, wait_interval, repetition):
        for _ in range(repetition):
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, runt=True, desired_frame_size=45)
            time.sleep(wait_interval)
            tl1s.vport_send_undersize_packets(traffic_item_name=traffic_item_name, runt=False, desired_frame_size=45)
            
    
    def vport_increment_decrement_frequency(vports, wait_interval, repetition):
        for _ in range(repetition):
            tl1s.vport_increment_decrement_frequency(vports=vports, operation="increment", step_size=70)
            time.sleep(wait_interval)
            tl1s.vport_increment_decrement_frequency(vports=vports, operation="decrement", step_size=60)
        
        
    
        
    print("==Link Up Down==")
    link_up_down(vports=["Port_1"], wait_interval=1, repetition=2)
    
    print("==Laser On Off==")
    laser_on_off(vports=["Port_1"], wait_interval=5, repetition=2)
    
    print("==Generating Faults==")
    generate_faults(vports=["Port_1"], wait_interval=5, repetition=1)
    
    print("==Generating Clock Faults==")
    vport_clock_source_faults_toggle(vports=["Port_1"], wait_interval=5, repetition=2)
    
    print("==Increment Decrement Transmit Deviation by PPM values==")
    vport_increment_decrement_frequency(vports=["Port_1"], wait_interval=5, repetition=2)


    
    print("==Generating undersize packets==")
    generate_undersize_packets_traffic(traffic_item_name, wait_interval=5, repetition=2)
    
    print("==Generating RUNT packets==")
    generate_runt_traffic(traffic_item_name,wait_interval=5, repetition=2)
    
    print("==Generating packets with CRC errors=")
    generate_crc_error_traffic(traffic_item_name, wait_interval=5, repetition=2)
    
    
    """Sample Output:
       ---------------
        (ixn-venv) ashwjosh@C0HD4NKHCX IxSampleScripts % python sample.py  
        ==Link Up Down==
        Port_1 turned down
        Port_1 turned up
        Port_1 turned down
        Port_1 turned up
        ==Laser On Off==
        Port_1 turned down
        Port_1 turned up
        Port_1 turned down
        Port_1 turned up
        ==Generating Faults==
        NovusHundredGigLan[0]: /api/v1/sessions/12/ixnetwork/vport/1/l1Config/novusHundredGigLan
                AutoInstrumentation: endOfFrame
                BadBlocksNumber: 4
                EnableAutoNegotiation: False
                EnablePPM: True
                EnableRsFec: True
                EnableRsFecStats: True
                EnabledFlowControl: True
                FirecodeAdvertise: False
                FirecodeForceOff: False
                FirecodeForceOn: False
                FirecodeRequest: False
                FlowControlDirectedAddress: 01 80 C2 00 00 01
                ForceDisableFEC: False
                GoodBlocksNumber: 0
                IeeeL1Defaults: False
                LaserOn: True
                LinkTraining: False
                LoopContinuously: True
                LoopCountNumber: 1
                Loopback: True
                LoopbackMode: internalLoopback
                Ppm: 70
                RsFecAdvertise: False
                RsFecForceOn: False
                RsFecRequest: False
                SendSetsMode: typeAOnly
                Speed: speed100g
                StartErrorInsertion: True
                TxIgnoreRxLinkFaults: False
                TypeAOrderedSets: localFault
                TypeBOrderedSets: remoteFault
                UseANResults: False
        NovusHundredGigLan[0]: /api/v1/sessions/12/ixnetwork/vport/1/l1Config/novusHundredGigLan
                AutoInstrumentation: endOfFrame
                BadBlocksNumber: 4
                EnableAutoNegotiation: False
                EnablePPM: True
                EnableRsFec: True
                EnableRsFecStats: True
                EnabledFlowControl: True
                FirecodeAdvertise: False
                FirecodeForceOff: False
                FirecodeForceOn: False
                FirecodeRequest: False
                FlowControlDirectedAddress: 01 80 C2 00 00 01
                ForceDisableFEC: False
                GoodBlocksNumber: 0
                IeeeL1Defaults: False
                LaserOn: True
                LinkTraining: False
                LoopContinuously: True
                LoopCountNumber: 1
                Loopback: True
                LoopbackMode: internalLoopback
                Ppm: 70
                RsFecAdvertise: False
                RsFecForceOn: False
                RsFecRequest: False
                SendSetsMode: typeBOnly
                Speed: speed100g
                StartErrorInsertion: True
                TxIgnoreRxLinkFaults: False
                TypeAOrderedSets: localFault
                TypeBOrderedSets: remoteFault
                UseANResults: False
        ==Generating Clock Faults==
        Loopback mode: internalLoopback
        Loopback mode: none
        Loopback mode: none
        Loopback mode: lineLoopback
        Loopback mode: lineLoopback
        Loopback mode: internalLoopback
        Loopback mode: internalLoopback
        Loopback mode: none
        Loopback mode: none
        Loopback mode: lineLoopback
        Loopback mode: lineLoopback
        Loopback mode: internalLoopback
        ==Increment Decrement Transmit Deviation by PPM values==
        PPM Enabled: True
        70
        New Value: 70
        PPM Enabled: True
        PPM Enabled: True
        70
        New Value: 70
        PPM Enabled: True
        PPM Enabled: True
        70
        New Value: 70
        PPM Enabled: True
        PPM Enabled: True
        70
        New Value: 70
        PPM Enabled: True
        ==Generating undersize packets==
        ==Generating RUNT packets==
        ConfigElement[0]: /api/v1/sessions/12/ixnetwork/traffic/trafficItem/8/configElement/1
                Crc: goodCrc
                DestinationMacMode: manual
                EnableDisparityError: False
                EncapsulationName: Ethernet.VLAN.IPv4
                EndpointSetId: 1
                PreambleCustomSize: 8
                PreambleFrameSizeMode: auto
        ConfigElement[0]: /api/v1/sessions/12/ixnetwork/traffic/trafficItem/8/configElement/1
                Crc: goodCrc
                DestinationMacMode: manual
                EnableDisparityError: False
                EncapsulationName: Ethernet.VLAN.IPv4
                EndpointSetId: 1
                PreambleCustomSize: 8
                PreambleFrameSizeMode: auto
        ==Generating packets with CRC errors=
        ConfigElement[0]: /api/v1/sessions/12/ixnetwork/traffic/trafficItem/8/configElement/1
                Crc: goodCrc
                DestinationMacMode: manual
                EnableDisparityError: False
                EncapsulationName: Ethernet.VLAN.IPv4
                EndpointSetId: 1
                PreambleCustomSize: 8
                PreambleFrameSizeMode: auto
        ConfigElement[0]: /api/v1/sessions/12/ixnetwork/traffic/trafficItem/8/configElement/1
                Crc: goodCrc
                DestinationMacMode: manual
                EnableDisparityError: False
                EncapsulationName: Ethernet.VLAN.IPv4
                EndpointSetId: 1
                PreambleCustomSize: 8
                PreambleFrameSizeMode: auto
        (ixn-venv) ashwjosh@C0HD4NKHCX IxSampleScripts % 
        """
