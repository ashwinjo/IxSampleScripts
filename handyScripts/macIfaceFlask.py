from flask import jsonify
from flask import Flask
import netifaces as ni

app = Flask(__name__)

@app.route('/interfacemacs/')
def interfacemacs():
    return jsonify(get_interfaces_and_mac_addresses())

def get_interfaces_and_mac_addresses():
    try:
        interfaces = ni.interfaces()
        interface_details = {}

        for iface in interfaces:
            iface_data = {}
            if iface.startswith('ens'):
                mac_address = ni.ifaddresses(iface).get(ni.AF_LINK)
                if mac_address:
                       mac_address = mac_address[0]['addr']
                else:
                       mac_address = 'N/A'
                iface_data.update({"mac": mac_address})
                import subprocess

                command = f"ethtool -i {iface} | grep bus-info"
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                iface_data.update({"bus_info": result.stdout.split()[-1]})
                interface_details[iface] = iface_data
                # Print the standard output and standard error
        return interface_details
    except Exception as e:
        print(f"Error: {e}")
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
