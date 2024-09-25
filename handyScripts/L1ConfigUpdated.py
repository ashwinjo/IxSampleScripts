from ixnetwork_restpy import SessionAssistant

linuxAPIServer = '10.36.74.13'
linuxAPIServerUsername = 'admin'
linuxAPIServerPassword = 'XXXXXXX'

# Creating IxNetworkSession
session_assistant = SessionAssistant(IpAddress=linuxAPIServer, UserName=linuxAPIServerUsername, Password=linuxAPIServerPassword,
    LogLevel=SessionAssistant.LOGLEVEL_INFO,
    SessionId=1,
    ClearConfig=False)

# Creating IxNetwork Object
ixnetwork = session_assistant.Ixnetwork

RxOutputPreTap = ixnetwork.Vport.find().TapSettings.find().Parameter.find(Name="RxOutputPreTap")
RxOutputPreTap.update(CurrentValue="5")

RxOutputAmp = ixnetwork.Vport.find().TapSettings.find().Parameter.find(Name="RxOutputAmp")
RxOutputAmp.update(CurrentValue="10")

RxOutputPostTap = ixnetwork.Vport.find().TapSettings.find().Parameter.find(Name="RxOutputPostTap")
RxOutputPostTap.update(CurrentValue="9")

ExplicitControl = ixnetwork.Vport.find().TapSettings.find().Parameter.find(Name="ExplicitControl")
ExplicitControl.update(CurrentValue="0")


ixnetwork.Vport.find().SaveCustomDefaults()
