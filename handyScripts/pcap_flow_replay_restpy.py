#!/usr/bin/env python3
"""
Load a PCAP, isolate ONE specific flow, and transmit it from IxNetwork.

Why this shape:
  IxNetwork's REST/RestPy model has NO 'importPcapFile' operation on
  /traffic/trafficItem (verified against ixnetwork_restpy 1.11.0). The only
  file-import ops that exist are:
     - vport.Import(Files('port.prt'))   -> IxExplorer port/stream file
     - field.Import(Files('x.csv'), col) -> CSV value lists
     - resourceManager.ImportConfigFile  -> full config JSON
  So the reliable automation path is: parse the PCAP client-side (scapy),
  pick the flow, and push the raw bytes into a RAW traffic item using an
  Ethernet stack + a 'custom' header carrying the remaining frame bytes.

Requires:
  pip install ixnetwork_restpy scapy
"""

from scapy.utils import rdpcap
from scapy.layers.inet import IP, TCP, UDP
from ixnetwork_restpy import SessionAssistant, Files

# ----------------------------------------------------------------------------
# 1. USER SETTINGS
# ----------------------------------------------------------------------------
API_SERVER   = '10.10.10.5'      # Windows IxNetwork API server or Linux Web Edition
API_PORT     = 11009             # 11009 = Windows GUI/API, 443 = Linux Web Edition
CHASSIS_IP   = '10.10.10.20'
TX_PORT      = (CHASSIS_IP, 1, 1)
RX_PORT      = (CHASSIS_IP, 1, 2)

PCAP_FILE    = 'capture.pcap'

# The "specific flow" you want to replay - classic 5-tuple filter.
# Set any value to None to wildcard it.
FLOW = dict(src_ip='192.168.1.10',
            dst_ip='192.168.1.20',
            proto='tcp',          # 'tcp' | 'udp' | None
            src_port=None,
            dst_port=80)

MAX_FRAMES   = 100               # cap how many frames from the flow to push
LINE_RATE_PC = 10                # % line rate
FRAME_COUNT  = 1000              # frames to transmit per stream


# ----------------------------------------------------------------------------
# 2. PARSE THE PCAP AND EXTRACT THE FLOW
# ----------------------------------------------------------------------------
def matches(pkt, f):
    if IP not in pkt:
        return False
    ip = pkt[IP]
    if f['src_ip'] and ip.src != f['src_ip']:
        return False
    if f['dst_ip'] and ip.dst != f['dst_ip']:
        return False
    if f['proto'] == 'tcp':
        if TCP not in pkt:
            return False
        l4 = pkt[TCP]
    elif f['proto'] == 'udp':
        if UDP not in pkt:
            return False
        l4 = pkt[UDP]
    else:
        l4 = None
    if l4 is not None:
        if f['src_port'] and l4.sport != f['src_port']:
            return False
        if f['dst_port'] and l4.dport != f['dst_port']:
            return False
    return True


packets = rdpcap(PCAP_FILE)
frames = [bytes(p) for p in packets if matches(p, FLOW)][:MAX_FRAMES]
if not frames:
    raise SystemExit('No packets in %s matched the flow filter.' % PCAP_FILE)

print('Matched %d frames (of %d in capture)' % (len(frames), len(packets)))

# IxNetwork value lists require identical frame sizes inside one stream,
# so bucket the flow's frames by length -> one traffic item per length.
buckets = {}
for fr in frames:
    buckets.setdefault(len(fr), []).append(fr)
print('Frame-length buckets: %s' % {k: len(v) for k, v in buckets.items()})


# ----------------------------------------------------------------------------
# 3. CONNECT TO IXNETWORK
# ----------------------------------------------------------------------------
session = SessionAssistant(IpAddress=API_SERVER,
                           RestPort=API_PORT,
                           UserName='admin', Password='admin',
                           SessionName='pcap-replay',
                           ClearConfig=True,
                           LogLevel=SessionAssistant.LOGLEVEL_INFO)
ixn = session.Ixnetwork

vp_tx = ixn.Vport.add(Name='Tx')
vp_rx = ixn.Vport.add(Name='Rx')
session.TestPlatform.Sessions.find()  # keep-alive touch
ixn.AssignPorts([{'Arg1': TX_PORT[0], 'Arg2': TX_PORT[1], 'Arg3': TX_PORT[2]},
                 {'Arg1': RX_PORT[0], 'Arg2': RX_PORT[1], 'Arg3': RX_PORT[2]}],
                [], [vp_tx, vp_rx], True)


# ----------------------------------------------------------------------------
# 4. BUILD ONE RAW TRAFFIC ITEM PER FRAME-LENGTH BUCKET
# ----------------------------------------------------------------------------
def build_raw_ti(name, frame_list):
    ti = ixn.Traffic.TrafficItem.add(Name=name, TrafficType='raw')
    ti.EndpointSet.add(Sources=vp_tx.Protocols.find(),
                       Destinations=vp_rx.Protocols.find())
    ce = ti.ConfigElement.find()[0]

    first = frame_list[0]
    eth_hdr, payload_len = first[:14], len(first) - 14

    # --- Ethernet header: take DA/SA/EtherType straight from the capture ---
    eth = ce.Stack.find(StackTypeId='^ethernet$')
    def mac(b):   return ':'.join('%02x' % x for x in b)
    eth.Field.find(FieldTypeId='ethernet.header.destinationAddress').update(
        ValueType='singleValue', SingleValue=mac(eth_hdr[0:6]))
    eth.Field.find(FieldTypeId='ethernet.header.sourceAddress').update(
        ValueType='singleValue', SingleValue=mac(eth_hdr[6:12]))
    eth.Field.find(FieldTypeId='ethernet.header.etherType').update(
        ValueType='singleValue', SingleValue='%04x' % int.from_bytes(eth_hdr[12:14], 'big'))

    # --- Append a 'custom' header holding everything after the Ethernet hdr ---
    tmpl = ixn.Traffic.ProtocolTemplate.find(StackTypeId='^custom$')
    eth.Append(Arg2=tmpl)
    custom = ce.Stack.find(StackTypeId='^custom$')

    # NOTE: custom.header.length is expressed in BITS in the API browser.
    #       Verify once in the GUI Packet Editor for your build, then trust it.
    custom.Field.find(FieldTypeId='custom.header.length').update(
        ValueType='singleValue', SingleValue=str(payload_len * 8))

    data_field = custom.Field.find(FieldTypeId='custom.header.data')
    if len(frame_list) == 1:
        data_field.update(ValueType='singleValue',
                          SingleValue=frame_list[0][14:].hex())
    else:
        # Cycle through every captured frame of this length, one per packet.
        data_field.update(ValueType='valueList',
                          ValueList=[f[14:].hex() for f in frame_list])

    ce.FrameRate.update(Type='percentLineRate', Rate=LINE_RATE_PC)
    ce.TransmissionControl.update(Type='fixedFrameCount', FrameCount=FRAME_COUNT)
    ce.FrameSize.update(Type='fixed', FixedSize=len(first))
    return ti


for length, frame_list in buckets.items():
    ti = build_raw_ti('PcapFlow_%dB' % length, frame_list)
    ixn.info('Created %s with %d frame variant(s)' % (ti.Name, len(frame_list)))


# ----------------------------------------------------------------------------
# 5. GENERATE / APPLY / RUN
# ----------------------------------------------------------------------------
ixn.Traffic.TrafficItem.find().Generate()
ixn.Traffic.Apply()
ixn.Traffic.StartStatelessTrafficBlocking()

stats = session.StatViewAssistant('Flow Statistics')
stats.CheckCondition('Tx Frames', StatViewAssistant.GREATER_THAN, 0, timeout=60)
for row in stats.Rows:
    print('%-30s Tx=%s Rx=%s Loss=%s' % (row['Traffic Item'], row['Tx Frames'],
                                         row['Rx Frames'], row['Loss %']))

ixn.Traffic.StopStatelessTrafficBlocking()

# Optional: persist for GUI inspection
# ixn.SaveConfig(Files('pcap_flow_replay.ixncfg', local_file=True))
