"""
manageSessions.py

   Connect to a Linux API server
      - View or delete open sessions

Supports IxNetwork API servers:
   - Windows, Windows Connection Mgr and Linux

Requirements
   - IxNetwork 8.50
   - Python 2.7 and 3+
   - pip install requests
   - pip install -U --no-cache-dir ixnetwork_restpy

Script development API doc:
   - The doc is located in your Python installation site-packages/ixnetwork_restpy/docs/index.html
   - On a web browser:
         - If installed in Windows: enter: file://c:/<path_to_ixnetwork_restpy>/docs/index.html
         - If installed in Linux: enter: file:///<path_to_ixnetwork_restpy>/docs/index.html
"""

import sys
import pandas
# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform


def get_session_information(testPlatform, Id):
        # Show all open sessions
        session_list = []
        for session in testPlatform.Sessions.find():
            sessionId = session[0].Id
            session_info = testPlatform.Sessions.find(Id=sessionId)
            ixNetwork = session_info.Ixnetwork.Globals
            sessionName = session_info.Name
            exceedsThreshold = check_if_session_greater_than_thresholds(ixNetwork.SessionUpTime)
            session_list.append({"sessionId": sessionId, 
                                 "sessionName": sessionName,
                                 "sessionUser":ixNetwork.Username,
                                 "sessionUptime": ixNetwork.SessionUpTime,
                                 "exceedsThreshold": str(exceedsThreshold)})
        return session_list
                

def deleteSession(testPlatform, Id):
    # Delete a particular session ID
    testPlatform.Sessions.find(Id=Id).remove()
    
    
def check_if_session_greater_than_thresholds(uptime):
    from  datetime import datetime, timedelta
    days = uptime.split()[0]
    hours = uptime.split()[2]

    if int(days) > 2:
        return False
    return True


def main(operation=None, Id=None):
    osPlatform = 'linux'

    if len(sys.argv) > 1:
        # Command line input: windows, windowsConnectionMgr or linux
        osPlatform = sys.argv[1]

    # Change API server values to use your setup
    if osPlatform == 'windowsConnectionMgr':
        platform = 'windows'
        apiServerIp = '192.168.70.3'
        apiServerPort = 11009

    # Change API server values to use your setup
    if osPlatform == 'linux':
        platform = 'linux'
        apiServerIp = '10.36.236.121'
        apiServerPort = 443
        username = 'admin'
        password = 'Kimchi123Kimchi123!'

    try:
        testPlatform = TestPlatform(apiServerIp, rest_port=apiServerPort, platform=platform)
        # authenticate with username and password
        testPlatform.Authenticate(username, password)
        
        if operation == "show":
            session_list = get_session_information(testPlatform, Id)
            print(pandas.DataFrame(session_list))
        if operation == "remove":
            deleteSession(testPlatform, Id)            
    except Exception as errMsg:
        print('\nrestPy.Exception:', errMsg)


if __name__ == "__main__":
    main(operation="show")
