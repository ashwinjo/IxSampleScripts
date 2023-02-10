import json
import tabulate
import pandas as pd
from  RestApi.IxOSRestInterface import IxRestSession

CHASSIS_LIST = ["10.36.236.121"]

def get_owned_ports(port_data_list):
    op = [item for item in port_data_list if item.get("owner")]
    # print (pd.DataFrame(op))
    return len(op), op


def start_stats_fetch(CHASSIS_LIST):
    for CHASSIS in CHASSIS_LIST:
        get_chassis_metrics(CHASSIS)

def get_chassis_metrics(CHASSIS):
    session = IxRestSession(CHASSIS, verbose=False)
    port_obj = dict()
    port_data_list = list()
    chassis_filter_dict = {}
    temp_dict = {}

    # Get all chassis/cards/ports
    chassisInfo = session.get_chassis()
    d = json.loads(json.dumps(chassisInfo.data[0]))
    list_of_ixos_protocols = d["ixosApplications"]
    for item in list_of_ixos_protocols:
        temp_dict.update({item["name"]: item["version"]})
    
    chassis_filter_dict.update(temp_dict)
    chassis_filter_dict.update({"chassisSerielNumber": d["serialNumber"],
                                "type": d["type"],
                                "numberOfPhysicalCards": str(d["numberOfPhysicalCards"]),
                                "managementIp":d["managementIp"],
                                })
    df = pd.DataFrame(chassis_filter_dict, index=[0])
    print(tabulate.tabulate(df, tablefmt='grid', showindex=False, headers=list(chassis_filter_dict.keys())))
    
    if  type(chassisInfo.data) != type([]) or 'state' not in chassisInfo.data[0]:
        print("Unexpected chassis response. Please check that you are connection to an IxOS chassis running 8.50 or newer version.")
    elif chassisInfo.data[0]['state'].upper() != 'UP':
        #chassis is not ready. need to take action
        print("Chassis {0} is reachable, but IxServer in down! Please check chassis connectivity, license avilability and logs.".format(CHASSIS))
    else: 
        card_list= session.get_cards().data
        port_list = session.get_ports().data
        

        for port in port_list:
            port_data_list.append(port)
        
        # Cards on Chassis
        sorted_cards = sorted(card_list, key=lambda d: d['cardNumber'])
        df = pd.DataFrame(sorted_cards)
        print(tabulate.tabulate(df, tablefmt='grid', showindex=False, headers=["serialNumber","numberOfPorts", 
                                                                               "displayName", "type", "parentId", "revision", 
                                                                               "MFGdatecode", "id", "state", "assemblyNumber", 
                                                                               "Card Number"]))
        
        # Ports on Chassis
        total_ports = len(port_data_list)
        df = pd.DataFrame(port_data_list)
        # print(tabulate.tabulate(df, tablefmt='grid', showindex=False, headers=['owner', 'transceiverModel', 'captureState', 'ownedState', 
        #                                                                        'simulatedCableState', 'type', 'portMemory', 'pcpuStatus', 
        #                                                                        'fullyQualifiedPortName', 'transceiverManufacturer', 
        #                                                                        'portNumber', 'speed', 'parentId', 'linkState', 'managementIp', 
        #                                                                        'transmitState', 'transceiverSerialNumber', 'id', 'cardNumber']))
        
        # Metric 1: Port Owned vs Ports Free
        op_count, op_result = get_owned_ports(port_data_list)
        percent_ports_owned = (op_count/total_ports) * 100
        
        print("% ports owned total",  percent_ports_owned)
        
        # Metric 2: Users on Chassis + #ports used
        list_of_users = [user["owner"].split("/")[-1] for user in op_result]
        for x in set(list_of_users):
            print ("{0}:--{1}".format(x, list_of_users.count(x)))
            
            
start_stats_fetch(CHASSIS_LIST)
