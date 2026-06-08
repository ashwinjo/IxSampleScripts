from ixnetwork_restpy import SessionAssistant, Files
import time

# The following code represents how you can connect to the session using Session Assistant
session_assistant = SessionAssistant(IpAddress="10.36.199.100", 
                                     RestPort=443,
                                     UserName="admin",
                                     Password="XXXXXXXXX", 
                                     LogLevel=SessionAssistant.LOGLEVEL_INFO,
                                     SessionId=1,
                                     #SessionName="ADNT-Test",
                                     LogFilename="restpy.log", 
                                     ClearConfig=False)

ixn = session_assistant.Ixnetwork

# configFile = "config.ixncfg" # Name of your file

# ixn.info('Loading binary config: {}'.format(configFile))
# ixn.LoadConfig(Files(configFile, local_file=True))

# The below section shows how to add or access the current Node
framesize = ixn.Traffic.find().TrafficItem.find().HighLevelStream.find().FrameSize.find()
framesize.update(Type="random", RandomMax=9100, RandomMin=128)


framerate = ixn.Traffic.find().TrafficItem.find().HighLevelStream.find().FrameRate.find()
framerate.update(Rate=50, Type='percentLineRate')


ixn.Traffic.find().TrafficItem.find().Generate()
ixn.Traffic.Apply()
ixn.Traffic.StartStatelessTrafficBlocking()

time.sleep(5) # sleep for 5 seconds

ixn.Traffic.StopStatelessTrafficBlocking()

portStatistics = session_assistant.StatViewAssistant('Port Statistics')

for rowNumber,flowStat in enumerate(portStatistics.Rows):
        ixn.info('\n\nSTATS: {}\n\n'.format(flowStat))
        # Refere Stat Fiels below to select "key" you are interested in:
        # ixn.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}\n'.format(
        #     rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
        #     flowStat['Tx Frames'], flowStat['Rx Frames']))


"""
Stat Fields:


STATS: Row:1  View:Port Statistics  Sampled:2026-06-08 23:18:28.510192 UTC
        Stat Name: 10.36.199.100/Card01/Port04
        Port Name: Ethernet - 002
        Line Speed: 100GE
        Link State: Link Up
        Frames Tx.: 0
        Valid Frames Rx.: 1596062
        Frames Tx. Rate: 0
        Valid Frames Rx. Rate: 208236
        Data Integrity Frames Rx.: 0
        Data Integrity Errors: 0
        Bytes Tx.: 0
        Bytes Rx.: 47417544867
        Bits Sent: 0
        Bits Received: 379340358936
        Bytes Tx. Rate: 0
        Tx. Rate (bps): 0.000
        Tx. Rate (Kbps): 0.000
        Tx. Rate (Mbps): 0.000
        Bytes Rx. Rate: 6224535301
        Rx. Rate (bps): 49796282408.000
        Rx. Rate (Kbps): 49796282.408
        Rx. Rate (Mbps): 49796.282
        Scheduled Frames Tx.: 0
        Scheduled Frames Tx. Rate: 0
        Control Frames Tx: 0
        Control Frames Rx: 0
        Ethernet OAM Information PDUs Sent: 0
        Ethernet OAM Information PDUs Received: 0
        Ethernet OAM Event Notification PDUs Received: 0
        Ethernet OAM Loopback Control PDUs Received: 0
        Ethernet OAM Organisation PDUs Received: 0
        Ethernet OAM Variable Request PDUs Received: 0
        Ethernet OAM Variable Response Received: 0
        Ethernet OAM Unsupported PDUs Received: 0
        Rx Pause Priority Group 0 Frames: 0
        Rx Pause Priority Group 1 Frames: 0
        Rx Pause Priority Group 2 Frames: 0
        Rx Pause Priority Group 3 Frames: 0
        Rx Pause Priority Group 4 Frames: 0
        Rx Pause Priority Group 5 Frames: 0
        Rx Pause Priority Group 6 Frames: 0
        Rx Pause Priority Group 7 Frames: 0
        Misdirected Packet Count: 0
        CRC Errors: 0
        Fragments: 0
        Undersize: 0
        Oversize: 8685231
        RS-FEC Corrected Codeword Count: 0
        RS-FEC Uncorrected Codeword Count: 0
        RS-FEC Corrected Codeword Count Rate: 0
        RS-FEC Uncorrected Codeword Count Rate: 0
        L1 Line Rate Transmit (%): 0.000


"""
