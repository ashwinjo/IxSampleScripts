from ixnetwork_restpy.testplatform.testplatform import TestPlatform
import pandas as pd
import sys

def deleteSession(testPlatform, Id):
    # Delete a particular session ID
    testPlatform.Sessions.find(Id=Id).remove()
    print(f"====> Session ID {Id} Deleted")

def get_session_information(testPlatform, Id):
    session = testPlatform.Sessions.find(Id=Id)
    sessionStatus = "NOERROR"
   
    ixNetwork = session.Ixnetwork.Globals
    errorList = session.Ixnetwork.Globals.find().AppErrors.find().Error.find(ErrorLevel='kError')
    errorCount = session.Ixnetwork.Globals.find().AppErrors.find().ErrorCount
    list_of_errors = [a.Name for a in errorList]
    if list_of_errors: sessionStatus = "ERROR"
         
    sessionName = session.Name
    vports = session.Ixnetwork.Vport.find()
    port_info = []
    
    for index ,port in enumerate(vports):
            portobj = vports[index]
            connectionState = portobj.ConnectionState
            assignedDisplayName = portobj.AssignedToDisplayName
            port_info.append(f"{assignedDisplayName}_{connectionState}")
    
    return [Id, sessionName, sessionStatus, errorCount, list_of_errors, ixNetwork.Username]
        
def get_all_sessions():
    # Show all open sessions
    session_list = []
    for session in testPlatform.Sessions.find():
        sessionId = session[0].Id
        session_list.append(get_session_information(testPlatform, sessionId))
        
    df = pd.DataFrame(session_list, columns = ['sessionId', 'sessionName', 'sessionStatus', 'errorCount', 'ErrorList', 'User'])
    print("==== Existing Session Information ====")
    print(df.to_string(index=False))
    
    return session_list
    
def delete_sessions_in_state(session_list, state="error"):
    for sessionItem in session_list:
        if sessionItem[2].lower() == state:
            deleteSession(testPlatform, sessionItem[0])


osPlatform = 'linux'

# Change API server values to use your setup
if osPlatform == 'linux':
    platform = 'linux'
    apiServerIp = sys.argv[1]
    apiServerPort = 443
    username = sys.argv[2]
    password = sys.argv[3]

try:
    testPlatform = TestPlatform(apiServerIp, rest_port=apiServerPort, platform=platform)
    testPlatform.Authenticate(username, password)
    
    session_list = []
    session_list_before = get_all_sessions()
    delete_sessions_in_state(session_list_before)
    session_list_after = get_all_sessions()
    print(f"Sessions Deleted = {len(session_list_before) - len(session_list_after)}")

except Exception as errMsg:
       raise Exception(errMsg)
   

"""Sample Output

==== Existing Session Information ====
 sessionId       sessionName sessionStatus  errorCount                                                                                                                                                                                                              ErrorList                                  User
         3  IxNetwork Test 3       NOERROR           0                                                                                                                                                                                                                     []  IxNetwork/ixnetworkweb/admin-3-28261
         4  IxNetwork Test 4         ERROR           1                                                                                                                                                                                               [Ports forcefully taken]  IxNetwork/ixnetworkweb/admin-4-32172
        11 IxNetwork Test 11       NOERROR           0                                                                                                                                                                                                                     [] IxNetwork/ixnetworkweb/admin-11-10762
        12 IxNetwork Test 12       NOERROR           0                                                                                                                                                                                                                     [] IxNetwork/ixnetworkweb/admin-12-10908
        18 IxNetwork Test 18         ERROR           1                                                                                                                                                                                               [Ports forcefully taken]  IxNetwork/ixnetworkweb/admin-18-8492
        19 IxNetwork Test 19         ERROR           4 [Ports forcefully taken, No ports assigned to topology 'Topo1'. Please connect Ixia hardware., No ports assigned to topology 'Topo2'. Please connect Ixia hardware., No ports assigned. Please connect Ixia hardware.]  IxNetwork/ixnetworkweb/admin-19-9077
====> Session ID 4 Deleted
====> Session ID 18 Deleted
====> Session ID 19 Deleted
==== Existing Session Information ====
 sessionId       sessionName sessionStatus  errorCount ErrorList                                  User
         3  IxNetwork Test 3       NOERROR           0        []  IxNetwork/ixnetworkweb/admin-3-28261
        11 IxNetwork Test 11       NOERROR           0        [] IxNetwork/ixnetworkweb/admin-11-10762
        12 IxNetwork Test 12       NOERROR           0        [] IxNetwork/ixnetworkweb/admin-12-10908
Sessions Deleted = 3


"""
