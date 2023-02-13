import json
import tabulate
import pandas as pd
from  RestApi.IxOSRestInterface import IxRestSession


def get_owned_ports(port_data_list):
    op = [item for item in port_data_list if item.get("owner")]
    print("******************* Ports ownership details ***********************")
    print (pd.DataFrame(op))
    return len(op), op

    
def get_chassis_information(session):
    """ Fetch chassis information from RestPy
    """
    temp_dict = {}
    chassis_filter_dict = {}
    chassisInfo = session.get_chassis()
    d = json.loads(json.dumps(chassisInfo.data[0]))
    chassis_state = chassisInfo.data[0]['state'].upper()
    list_of_ixos_protocols = d["ixosApplications"]
    for item in list_of_ixos_protocols:
        temp_dict.update({item["name"]: item["version"]})
    
    chassis_filter_dict.update(temp_dict)
    chassis_filter_dict.update({"chassisSerielNumber": d["serialNumber"],
                                "controllerSerialNumber": d["controllerSerialNumber"],
                                "type": d["type"],
                                "numberOfPhysicalCards": str(d["numberOfPhysicalCards"]),
                                "state": chassis_state
                                })
    df = pd.DataFrame(chassis_filter_dict, index=[0])
    
    print("\n******************* Chassis Information ***********************\n")
    print(tabulate.tabulate(df, tablefmt='grid', showindex=False, headers=list(chassis_filter_dict.keys())))
    
def get_chassis_cards_information(session):
    """_summary_
    """
    card_list= session.get_cards().data
    
    # Cards on Chassis
    sorted_cards = sorted(card_list, key=lambda d: d['cardNumber'])
    df = pd.DataFrame(sorted_cards)
    print("\n******************* Chassis Card Information ***********************\n")
    print(tabulate.tabulate(df, tablefmt='grid', showindex=False, headers=["serialNumber","numberOfPorts", 
                                                                            "displayName", "type", "parentId", "revision", 
                                                                            "MFGdatecode", "id", "state", "assemblyNumber", 
                                                                            "Card Number"]))
def get_chassis_ports_information(session):
    """_summary_
    """
    # Ports on Chassis
    port_data_list = []
    port_list = session.get_ports().data
    
    for port in port_list:
        port_data_list.append(port)
    total_ports = len(port_list)
    
    
        
    # Metric 1: Port Owned vs Ports Free
    op_count, op_result = get_owned_ports(port_data_list)
    free_ports = total_ports - op_count
    percent_ports_owned = (op_count/total_ports) * 100
    percent_ports_free = (free_ports/total_ports) * 100
    
    print("\n******************* Percentage ports having owners ***********************\n")
    print("% ports owned total",  percent_ports_owned)
    print("% ports free total",  percent_ports_free)


    # Metric 2: Users on Chassis + #ports used
    list_of_users = [user["owner"].split("/")[-1] for user in op_result]
    print("\n******************* Users on Chassis ***********************\n")
    for x in set(list_of_users):
        print ("{0}:--{1}".format(x, list_of_users.count(x)))


def start_chassis_rest_data_fetch(chassis, username, password):
    session = IxRestSession("10.36.236.121", username= "admin", password="Kimchi123Kimchi123!", verbose=False)
    get_chassis_information(session)
    get_chassis_cards_information(session)
    get_chassis_ports_information(session)
    



