from ixnetwork_restpy import SessionAssistant 
import time


class TestL1Settings(object):

    def __init__(self, ipaddr, user, password, session_id):
        """Constructor for TestCase CLasses
        Args:
            ipaddr (_type_): ip of ixia chasses
            user (_type_): username for ixia chassis
            password (_type_): password for ixia chassis
            session_name (_type_): session name on Ixia Linux chassis to connect to
        """
        session_assistant =SessionAssistant(ipaddr, 
                        UserName=user, 
                        Password= password,
                        SessionId=session_id,
                        LogLevel=SessionAssistant.LOGLEVEL_INFO, 
                        ClearConfig=False)

        self.ixnetwork = session_assistant.Ixnetwork
    

    def vport_link_up_down(self, **kwargs):
        """Turn L1 Ports UP/Down
        Returns:
            _type_: _description_
        """
        res = ""
        vport_name = kwargs.get("vports")[0]
        far_port = kwargs.get("vports")[1]
        operation =  kwargs.get("operation")
        vport = self.ixnetwork.Vport.find(Name=vport_name)
        fvport = self.ixnetwork.Vport.find(Name=far_port)
        print("Far Port:", fvport.State)
        vport.LinkUpDn(Arg2=operation)
        while True:
            fvport = self.ixnetwork.Vport.find(Name=far_port)
            ast = fvport.State
            if ast == operation:
                print("Far Port:", fvport.State)
                break
            
    

if __name__ == "__main__":
    
    """
    Prerequisite, create a sessions, add 2 ports,connect them and name them Port_1, Port_2 from L1 Settings tab.
    If you do not want to change the port names, edit line 74 with your port names
    """
    
    # When connecting to Linux API Server
    tl1s = TestL1Settings(ipaddr='10.36.236.121', user='admin',
                          password='XXXXXXXXXXXXXXXX!', session_id=<session_id>)
    
       
    def link_up_down(vports):
        
        import time
        # Set the start time
        start_time = time.time()

        # Run the loop for one minute (60 seconds)
        ctr = 0
        while time.time() - start_time < 60:
            tl1s.vport_link_up_down(vports=vports, operation="down")
            tl1s.vport_link_up_down(vports=vports, operation="up")
            ctr +=1
            print(ctr)
            
        print(f"Flip rate is {ctr} flaps/minute")
    link_up_down(vports=["Port_1", "Port_2"])

""" ========== Output ================

PS C:\Users\ashwjosh\Downloads\Batch> & C:/Python3/python.exe c:/Users/ashwjosh/Downloads/Batch/Batch/linkflap.py
2023-10-04 19:27:45 [ixnetwork_restpy.connection tid:24672] [INFO] using python version 3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)]
2023-10-04 19:27:45 [ixnetwork_restpy.connection tid:24672] [INFO] using ixnetwork-restpy version 1.1.10
2023-10-04 19:27:45 [ixnetwork_restpy.connection tid:24672] [WARNING] Verification of certificates is disabled
2023-10-04 19:27:45 [ixnetwork_restpy.connection tid:24672] [INFO] Determining the platform and rest_port using the 10.36.236.121 address...
2023-10-04 19:27:47 [ixnetwork_restpy.connection tid:24672] [WARNING] Unable to connect to http://10.36.236.121:11009.
2023-10-04 19:27:49 [ixnetwork_restpy.connection tid:24672] [WARNING] Unable to connect to https://10.36.236.121:11009.
2023-10-04 19:27:50 [ixnetwork_restpy.connection tid:24672] [WARNING] Unable to connect to http://10.36.236.121:443.
2023-10-04 19:27:50 [ixnetwork_restpy.connection tid:24672] [INFO] Connection established to `https://10.36.236.121:443 on linux`
2023-10-04 19:27:51 [ixnetwork_restpy.connection tid:24672] [INFO] Using IxNetwork api server version 9.30.2212.7
2023-10-04 19:27:51 [ixnetwork_restpy.connection tid:24672] [INFO] User info IxNetwork/ixnetworkweb/admin-1-4268
Far Port: up
Far Port: down
Far Port: down
Far Port: up
1
Far Port: up
Far Port: down
Far Port: down
Far Port: up
2
Far Port: up
Far Port: down
Far Port: down
Far Port: up
3
Far Port: up
Far Port: down
Far Port: down
Far Port: up
4
Far Port: up
Far Port: down
Far Port: down
Far Port: up
5
Far Port: up
Far Port: down
Far Port: down
Far Port: up
6
Far Port: up
Far Port: down
Far Port: down
Far Port: up
7
Far Port: up
Far Port: down
Far Port: down
Far Port: up
8
Far Port: up
Far Port: down
Far Port: down
Far Port: up
9
Far Port: up
Far Port: down
Far Port: down
Far Port: up
10
Far Port: up
Far Port: down
Far Port: down
Far Port: up
11
Far Port: up
Far Port: down
Far Port: down
Far Port: up
12
Flip rate is 12 flaps/minute

========="""

