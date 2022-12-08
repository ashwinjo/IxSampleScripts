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
    

    def vport_link_up_down(self, **kwargs):
        """_summary_

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
        """_summary_

        Returns:
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
        """_summary_
        """
        vports = kwargs.get("vports")
        source_value =  kwargs.get("source_value")
        dest_value = kwargs.get("dest_value")
        send_sets_mode =  kwargs.get("send_sets_mode")
        
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            vp = vport.L1Config.find().NovusHundredGigLan.find()

            # localFault | remoteFault
            vp.TypeAOrderedSets = source_value
            vp.TypeBOrderedSets = dest_value

            # alternate | typeAOnly | typeBOnly
            vp.SendSetsMode = send_sets_mode

            vp.StartErrorInsertion = True
            print(vp)
            

    def vport_increment_decrement_frequency(self, vports: List, operation: str, step_size: int):
        """_summary_

        Args:
            vports (List): _description_
            operation (str): _description_
            step123 (int): _description_
        """
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)

            vport.L1Config.find().NovusHundredGigLan.find().EnablePPM = True
            print(
                f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")

            print(vport.L1Config.NovusHundredGigLan.Ppm)
            if operation == "increment":
                vport.L1Config.find().NovusHundredGigLan.find().Ppm = step_size
                print(f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")

            elif operation == "decrement":
                vport.L1Config.find().NovusHundredGigLan.find(
                ).Ppm = f"-{step_size}"
                print(f"New Value: {vport.L1Config.NovusHundredGigLan.Ppm}")

            vport.L1Config.find().NovusHundredGigLan.find().EnablePPM
            import time
            time.sleep(10)
            print(
                f"PPM Enabled: {vport.L1Config.NovusHundredGigLan.EnablePPM}")

    def vport_clock_source_faults(self, **kwargs):
        """_summary_
        """
        vports = kwargs.get("vports")
        operation =  kwargs.get("source_value")
        for vport_name in vports:
            vport = self.ixnetwork.Vport.find(Name=vport_name)
            print(
                f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")
            vport.L1Config.find().NovusHundredGigLan.find().LoopbackMode = operation
            print(
                f"Loopback mode: {vport.L1Config.NovusHundredGigLan.LoopbackMode}")

    def vport_send_undersize_packets(self, **kwargs):
        """_summary_
        """
        create_traffic_item = kwargs.get("create_traffic_item")
        traffic_item_name = kwargs.get("traffic_item_name")
        undersize = kwargs.get("undersize")
        runt = kwargs.get("runt")
        crc = kwargs.get("crc")
        desired_frame_size = kwargs.get("desired_frame_size")
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
                configElement.Crc = 'badCrc'
                
                print(configElement)


if __name__ == "__main__":
    tl1s = TestL1Settings(ipaddr='10.36.236.121', user='admin',
                          password='Kimchi123Kimchi123!', session_id='12', 
                          clear_config=False)



    configuration_template = {
        "functions": [
        {
            "method_name": tl1s.vport_laser_on_off,
            "kwargs": {
                "vports": ["Port_1"],
                "operation": "on"
            },
            "repeat": 1,
            "enable": True,
            "wait": 5 #TODO
        },
        {
            "method_name": tl1s.vport_laser_on_off,
            "kwargs": {
                "vports": ["Port_1"],
                "operation": "off"
            },
            "repeat": 1,
            "enable": True,
            "wait": 5
        },
        {
            "method_name": tl1s.vport_link_up_down,
            "kwargs": {
                "vports": ["Port_1"],
                "operation": "up"
            },
            "repeat": 3,
            "enable": True
        },
        {
            "method_name": tl1s.vport_link_up_down,
            "kwargs": {
                "vports": ["Port_1"],
                "operation": "down"
            },
            "repeat": 3,
            "enable": True
        },
        {
            "method_name": tl1s.vport_insert_local_fault,
            "kwargs": {
                "vports": ["Port_1"],
                "source_value": "localFault",
                "dest_value": "remoteFault",
                "send_sets_mode": "typeAOnly"
            },
            "repeat": 1,
            "enable": True
        },
        {
            "method_name": tl1s.vport_increment_decrement_frequency,
            "kwargs": {
                "vports": ["Port_1"],
                "operation": "increment",
                "step_size": 75
            },
            "repeat": 1,
            "enable": True
        },
        {
            "method_name": tl1s.vport_send_undersize_packets,
            "kwargs": {
                "traffic_item_name" : "TI",
                "undersize" : True,
                "runt" : False,
                "crc" : False, 
                "desired_frame_size" : 40 
            },
            "repeat": 1,
            "enable": True
        },
        {
            "method_name": tl1s.vport_send_undersize_packets,
            "kwargs": {
                "traffic_item_name" : "TI",
                "runt" : True,
                "desired_frame_size" : 60
            },
            "repeat": 1,
            "enable": True
        },
        {
            "method_name": tl1s.vport_send_undersize_packets,
            "kwargs": {
                "traffic_item_name" : "TI",
                "crc" : True, 
            },
            "repeat": 1,
            "enable": True
        }
                ]
    }


    for vals in configuration_template["functions"]:
        method_name = vals["method_name"].__name__
        method_object = vals["method_name"]
        enabled = vals["enable"]
        params = vals["kwargs"]
        
        if enabled:
            for iteration in range(vals["repeat"]):
                
                if method_name in ["vport_laser_on_off", "vport_link_up_down", "vport_clock_source_faults"]:
                    method_object(vports=params["vports"], operation=params["operation"])
                    
                if method_name in ["vport_insert_local_fault"]:
                    method_object(vports=params["vports"], 
                                source_value=params["source_value"],
                                dest_value=params["dest_value"],
                                send_sets_mode=params["send_sets_mode"])
                    
                if method_name in ["vport_increment_decrement_frequency"]:
                    method_object(vports=params["vports"], 
                                operation=params["operation"],
                                step_size=params["step_size"])
                    
                if  method_name in ['vport_send_undersize_packets']:
                    method_object(create_traffic_item = params.get("create_traffic_item", False),
                                traffic_item_name=params.get("create_traffic_item", "TI"), 
                                undersize=params.get("undersize", False), 
                                runt=params.get("runt", False),
                                crc=params.get("crc", False), 
                                desired_frame_size=params.get("desired_frame_size", 128))
            
            

        """
        # print (tl1s.vport_laser_on_off(vports=['Port_1'], operation="on"))

        # print (tl1s.vport_link_up_down(vports=['Port_1'], operation="down"))
        # print (tl1s.vport_link_up_down(vports=['Port_2'], operation="down"))

        # print (tl1s.vport_link_up_down(vports=['Port_1'], operation="up"))
        # print (tl1s.vport_link_up_down(vports=['Port_2'], operation="up"))

        # tl1s.vport_increment_decrement_frequency(vports=['Port_1'], operation="increment", step123=70)
        # tl1s.vport_clock_source_faults(vports=['Port_1','Port_2'], loopback_mode='lineLoopback')

        #tl1s.vport_insert_local_fault(vports=['Port_1'], ssource_value='localFault',dest_value='remoteFault',send_sets_mode="typeAOnly")

        # tl1s.vport_send_undersize_packets(traffic_item_name="TI", undersize=True, desired_frame_size=60)
        # tl1s.vport_send_undersize_packets(traffic_item_name="TI", runt=True, desired_frame_size=45)
        # tl1s.vport_send_undersize_packets(traffic_item_name="TI", crc=True, desired_frame_size=128)

        """
     
 