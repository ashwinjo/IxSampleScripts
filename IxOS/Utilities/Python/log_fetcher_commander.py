
from IxOSRest import start_chassis_rest_data_fetch
from IxOSSHFetch import get_linux_chassis_information_from_cli


def start_chassis_data_fetch(CHASSIS_LIST):
    for chassis in CHASSIS_LIST:
        start_chassis_rest_data_fetch(chassis["ip"], chassis["username"], chassis["password"])
        get_linux_chassis_information_from_cli(chassis["ip"], chassis["username"], chassis["password"])



CHASSIS_LIST = [{
    "ip": "X.X.X.X",
    "username": "admin",
    "password": "xxxxx"
}]

start_chassis_data_fetch(CHASSIS_LIST)