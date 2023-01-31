import json
import pandas as pd
from  RestApi.IxOSRestInterface import IxRestSession

CHASSIS = "10.36.236.121" #replace this with your chassis address/hostname.


def get_owned_ports(port_data_list):
    op = [item for item in port_data_list if item.get("owner")]
    # print (pd.DataFrame(op))
    return len(op), op

session = IxRestSession(CHASSIS, verbose=False)
port_obj = dict()
port_data_list = list()

# Get all chassis/cards/ports
chassisInfo = session.get_chassis()

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
    sorted_footballers_by_goals = sorted(card_list, key=lambda d: d['cardNumber']) 
    print(pd.DataFrame(sorted_footballers_by_goals))
    
    # Ports on Chassis
    total_ports = len(port_data_list)
    print (pd.DataFrame(port_data_list))
    
    # Metric 1: Port Owned vs Ports Free
    op_count, op_result = get_owned_ports(port_data_list)
    percent_ports_owned = (op_count/total_ports) * 100
    
    print("% ports owned total",  percent_ports_owned)
    
    # Metric 2: Users on Chassis + #ports used
    list_of_users = [user["owner"].split("/")[-1] for user in op_result]
    for x in set(list_of_users):
        print ("{0}:--{1}".format(x, list_of_users.count(x)))