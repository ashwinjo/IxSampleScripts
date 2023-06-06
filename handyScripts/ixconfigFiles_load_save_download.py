# Import the RestPy module
from ixnetwork_restpy import SessionAssistant, Files

apiServerIp = '10.36.236.121'

# A list of chassis to use
ixChassisIpList = ['10.36.236.121']
portList = [[ixChassisIpList[0], 2, 15], [ixChassisIpList[0], 2, 16]]

# For Linux API server only
username = 'admin'
password = 'XXXXXXX'

# For linux and connection_manager only. Set to True to leave the session alive for debugging.
debugMode = False

# Forcefully take port ownership if the portList are owned by other users.
forceTakePortOwnership = True

configFile = 'abc_new_bgp_ngpf.ixncfg'
# Connect to the API server

# LogLevel: none, info, warning, request, request_response, all
session = SessionAssistant(IpAddress=apiServerIp, RestPort=None, UserName=username, Password=password, 
                            SessionName=None, SessionId=None, ApiKey=None,
                            ClearConfig=True, LogLevel='all', LogFilename='restpy.log')




ixNetwork = session.Ixnetwork
# Load a saved config file
ixNetwork.info('Loading config file: {0}'.format(configFile))
ixNetwork.LoadConfig(Files(configFile, local_file=True))


# Custom code based on customer use case

topology = ixNetwork.Topology.find()
topology.Name = "New Topology Name"

new_config_file_name = f"new_{configFile}"

# File will be uploaded to the server to the default file storage location.
ixNetwork.SaveConfig(Files(new_config_file_name, local_file=True))

# Get file from local server and download it to local file system.
session.Session.DownloadFile(new_config_file_name, f"abc_{new_config_file_name}")


    
