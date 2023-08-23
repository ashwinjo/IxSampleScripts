
import subprocess
import json
import requests



def run_rfc_test_for_sanity():
	command = "sh rfc2544_test_multiple_flows.sh"
	result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	if result.returncode == 0:
		print("Running rfc 2544 test")
		print(result.stdout)
	else:
		print("Error:", result.stderr)

def _get_pci_mac_interface_mappings(ip_address=None):
	url = f"http://{ip_address}:5000/interfacemacs/"
	try:
    		response = requests.get(url)
    		if response.status_code == 200:
        		return response.json()
    		else:
        		print(f"Request failed with status code: {response.status_code}")
	except requests.exceptions.RequestException as e:
    		print(f"An error occurred: {e}")

def create_source_destination_mac_lists(src_ip_address=None, dst_ip_address=None):
	list_of_macs = []

	dummy_macs_for_test =  [('XX:0c:29:b6:5e:b3', 'YY:0c:29:6b:2d:cd'), ('XX:0c:29:b6:5e:a9', 'YY:0c:29:6b:2d:c3')]

	nearend_map = _get_pci_mac_interface_mappings(src_ip_address)
	farend_map = _get_pci_mac_interface_mappings(dst_ip_address)
	set1 = set(nearend_map)
	set2 = set(farend_map)
	virtualinterfaces = set1.intersection(set2)

	for viface in virtualinterfaces:
		list_of_macs.append((nearend_map[viface]["mac"], farend_map[viface]["mac"]))

	return list_of_macs+dummy_macs_for_test


def get_pci_bus_address(command):
	result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
    		output = result.stdout.strip()
    		return output
	else:
    		error = result.stderr.strip()
    		print("Error:", error)


def run_docker_compose():
	command = "docker-compose -f docker-compose.yml up"
	result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	if result.returncode == 0:
    		print(result.stdout)
	else:
    		print("Error:", result.stderr)


def run_hugepages():
	command = "sh hugepages.sh"
	result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	if result.returncode == 0:
                print("Huge Pages Configuration Set")
	else:
		print("Error:", result.stderr)

def create_docker_compose():
	cmd1 = "lspci | grep VMXNET | awk 'NR==1{print $1}'"
	cmd2 = "lspci | grep VMXNET | awk 'NR==2{print $1}'"
	cmd3 = "lspci | grep VMXNET | awk 'NR==3{print $1}'"
	cmd4 = "lspci | grep VMXNET | awk 'NR==4{print $1}'"
	te_pci_map = {}


	pci_address_1 = "0000."+get_pci_bus_address(cmd1)
	pci_address_2 = "0000."+get_pci_bus_address(cmd2)
	pci_address_3 = "0000."+"abcde" 
	pci_address_4 = "0000."+"lmnop"

	te_pci_map["te1"] = pci_address_1
	te_pci_map["te2"] = pci_address_2
	te_pci_map["te3"] = pci_address_3
	te_pci_map["te4"] = pci_address_4
	print(te_pci_map)
	docker_compose_template=f"""version: '3'
services:
  te1-5551:
    image: ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
    container_name: TE1-5551
    network_mode: host
    privileged: true
    environment:
      OPT_LISTEN_PORT: 5551
      ARG_IFACE_LIST: "pci@{pci_address_1}"
    volumes:
      - /mnt/huge:/mnt/huge
      - /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages
      - /sys/bus/pci/drivers:/sys/bus/pci/drivers
      - /sys/devices/system/node:/sys/devices/system/node
      - /dev:/dev

  te2-5552:
    image: ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
    container_name: TE2-5552
    network_mode: host
    privileged: true
    environment:
      OPT_LISTEN_PORT: 5552
      ARG_IFACE_LIST: "pci@{pci_address_2}"
    volumes:
      - /mnt/huge:/mnt/huge
      - /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages
      - /sys/bus/pci/drivers:/sys/bus/pci/drivers
      - /sys/devices/system/node:/sys/devices/system/node
      - /dev:/dev

  te3-5553:
    image: ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
    container_name: TE2-5553
    network_mode: host
    privileged: true
    environment:
      OPT_LISTEN_PORT: 5553
      ARG_IFACE_LIST: "pci@{pci_address_3}"
    volumes:
      - /mnt/huge:/mnt/huge
      - /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages
      - /sys/bus/pci/drivers:/sys/bus/pci/drivers
      - /sys/devices/system/node:/sys/devices/system/node
      - /dev:/dev

  te4-5554:
    image: ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
    container_name: TE2-5554
    network_mode: host
    privileged: true
    environment:
      OPT_LISTEN_PORT: 5554
      ARG_IFACE_LIST: "pci@{pci_address_4}"
    volumes:
      - /mnt/huge:/mnt/huge
      - /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages
      - /sys/bus/pci/drivers:/sys/bus/pci/drivers
      - /sys/devices/system/node:/sys/devices/system/node
      - /dev:/dev

  Ixia-c-Controller:
    image: ghcr.io/open-traffic-generator/ixia-c-controller:0.0.1-361
    network_mode: host
    command: --accept-eula"""

	with open("docker-compose.yml", "w") as f:
		f.write(docker_compose_template)
	return te_pci_map

def create_settings_json(src_ip_address=None, dst_ip_address=None, controller_ip_address=None):
    settings = {
                    "username": "common",
                    "http_server": f"https://{controller_ip_address}:8443",
                    "grpc_server": f"{controller_ip_address}:40051",
                    "ports": [
                        f"{src_ip_address}:5551",
                        f"{src_ip_address}:5552",
                        f"{src_ip_address}:5553",
                        f"{src_ip_address}:5554",
			f"{dst_ip_address}:5551",
                        f"{dst_ip_address}:5552",
                        f"{dst_ip_address}:5553",
                        f"{dst_ip_address}:5554",
                    ],
                    "soft_dut": "localhost:22",
                    "speed": "speed_100_gbps",
                    "line_rate": 100,
                    "mtu": 9000,
                    "promiscuous": True,
                    "timeout_seconds": 300,
                    "interval_seconds": 1,
                    "log_level": "info",
                    "http_transport": True,
                    "dynamic_stats_output": True,
                    "capture_validation": False,
                    "flow_metric_validation": False
                    }
    with open("settings.json", 'w') as json_file:
            json.dump(settings, json_file, indent=4)


def create_unidirectional_flow_json(src_ip_address=None, dst_ip_address=None, mac_addresses_map=None):
    unidirectinal_flow_template = {
    "ports": [
        {
            "name": "VM1-TE1",
            "location": f"{src_ip_address}:5551"
        },
        {
            "name": "VM1-TE2",
            "location": f"{src_ip_address}:5552"
        },
        {
            "name": "VM1-TE3",
            "location": f"{src_ip_address}:5553"
        },
        {
            "name": "VM1-TE4",
            "location": f"{src_ip_address}:5554"
        },
        {
            "name": "VM2-TE1",
            "location": f"{dst_ip_address}:5551"
        },
        {
            "name": "VM2-TE2",
            "location": f"{dst_ip_address}:5552"
        },
        {
            "name": "VM2-TE3",
            "location": f"{dst_ip_address}:5553"
        },
        {
            "name": "VM2-TE4",
            "location": f"{dst_ip_address}:5554"
        }
    ],
    "layer1": [
        {
            "name": "l1",
            "port_names": [
                "VM1-TE1",
                "VM1-TE2",
                "VM1-TE3",
                "VM1-TE4",
                "VM2-TE1",
                "VM2-TE2",
                "VM2-TE3",
                "VM2-TE4"
            ],
            "speed": "speed_100_gbps"
        }
    ],
    "flows": [
        {
            "name": "f1 VM1-TE1 -> VM2-TE1",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE1",
                    "rx_name": "VM2-TE1"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 1518
            },
            "rate": {
                "choice": "percentage",
                "percentage": 3 
            },
            "duration": {
                "choice": "fixed_packets",
                "fixed_packets": {
                    "packets": 1000000
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[0][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[0][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f2 VM1-TE2 -> VM2-TE2",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE2",
                    "rx_name": "VM2-TE2"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 1518
            },
            "rate": {
                "choice": "percentage",
                "percentage": 3 
            },
            "duration": {
                "choice": "fixed_packets",
                "fixed_packets": {
                    "packets": 1000000
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[1][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[1][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f3 VM1-TE3 -> VM2-TE3",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE3",
                    "rx_name": "VM2-TE3"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 1518
            },
            "rate": {
                "choice": "percentage",
                "percentage": 3 
            },
            "duration": {
                "choice": "fixed_packets",
                "fixed_packets": {
                    "packets": 1000000
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[2][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[2][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f4 VM1-TE4 -> VM2-TE4",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE4",
                    "rx_name": "VM2-TE4"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 1518
            },
            "rate": {
                "choice": "percentage",
                "percentage": 3 
            },
            "duration": {
                "choice": "fixed_packets",
                "fixed_packets": {
                    "packets": 1000000
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[3][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[3][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        }
    ]
}
    try:
        with open("configs/ipv4_unidirectional_4_flows.json", 'w') as json_file:
            json.dump(unidirectinal_flow_template, json_file, indent=4)
        print("Data successfully written to configs/ipv4_unidirectional_4_flows.json")
    except Exception as e:
        print("Error writing data to configs/ipv4_unidirectional_4_flows.json: {e}")



def create_rfc_2544_throuput_json(src_ip_address=None, dst_ip_address=None, mac_addresses_map=None):
	rfc_2544_flow_template={
    "ports": [
        {
            "name": "VM1-TE1",
            "location": f"{src_ip_address}:5551"
        },
        {
            "name": "VM1-TE2",
            "location": f"{src_ip_address}:5552"
        },
        {
            "name": "VM1-TE3",
            "location": f"{src_ip_address}:5553"
        },
        {
            "name": "VM1-TE4",
            "location": f"{src_ip_address}:5554"
        },
        {
            "name": "VM2-TE1",
            "location": f"{dst_ip_address}:5551"
        },
        {
            "name": "VM2-TE2",
            "location": f"{dst_ip_address}:5552"
        },
        {
            "name": "VM2-TE3",
            "location": f"{dst_ip_address}:5553"
        },
        {
            "name": "VM2-TE4",
            "location": f"{dst_ip_address}:5554"
        }
    ],
    "layer1": [
        {
            "name": "l1",
            "port_names": [
                "VM1-TE1",
                "VM1-TE2",
                "VM1-TE3",
                "VM1-TE4",
                "VM2-TE1",
                "VM2-TE2",
                "VM2-TE3",
                "VM2-TE4"
            ],
            "speed": "speed_100_gbps"
        }
    ],
    "flows": [
        {
            "name": "f1 VM1-TE1 -> VM2-TE1",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE1",
                    "rx_name": "VM2-TE1"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 64
            },
            "rate": {
                "choice": "pps",
                "pps": 10000000
            },
            "duration": {
                "choice": "fixed_seconds",
                "fixed_seconds": {
                    "seconds": 15
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[0][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[0][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f2 VM1-TE2 -> VM2-TE2",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE2",
                    "rx_name": "VM2-TE2"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 64
            },
            "rate": {
                "choice": "pps",
                "pps": 10000000
            },
            "duration": {
                "choice": "fixed_seconds",
                "fixed_seconds": {
                    "seconds": 15
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[1][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[1][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f3 VM1-TE3 -> VM2-TE3",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE3",
                    "rx_name": "VM2-TE3"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 64
            },
            "rate": {
                "choice": "pps",
                "pps": 10000000
            },
            "duration": {
                "choice": "fixed_seconds",
                "fixed_seconds": {
                    "seconds": 15
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[2][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[2][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        },
        {
            "name": "f4 VM1-TE4 -> VM2-TE4",
            "tx_rx": {
                "choice": "port",
                "port": {
                    "tx_name": "VM1-TE4",
                    "rx_name": "VM2-TE4"
                }
            },
            "metrics": {
                "enable": True
            },
            "size": {
                "choice": "fixed",
                "fixed": 64
            },
            "rate": {
                "choice": "pps",
                "pps": 10000000
            },
            "duration": {
                "choice": "fixed_seconds",
                "fixed_seconds": {
                    "seconds": 15
                }
            },
            "packet": [
                {
                    "choice": "ethernet",
                    "ethernet": {
                        "dst": {
                            "choice": "value",
                            "value": mac_addresses_map[3][0]
                        },
                        "src": {
                            "choice": "value",
                            "value": mac_addresses_map[3][1]
                        }
                    }
                },
                {
                    "choice": "ipv4",
                    "ipv4": {
                        "dst": {
                            "choice": "value",
                            "value": "1.1.1.1"
                        },
                        "src": {
                            "choice": "value",
                            "value": "1.1.1.2"
                        }
                    }
                }
            ]
        }
    ]
}
	try:
		with open("configs/throughput_rfc2544_4_flows.json", 'w') as json_file:
			json.dump(rfc_2544_flow_template, json_file, indent=4)
			print("Data successfully written to configs/throughput_rfc2544_4_flows.json")
	except Exception as e:
		print("Error writing data to configs/throughput_rfc2544_4_flows.json: {e}")


mac_addresses_map = create_source_destination_mac_lists(src_ip_address="10.36.229.108", dst_ip_address="10.36.229.46")
run_hugepages()
create_docker_compose()
run_docker_compose()
create_settings_json(src_ip_address="10.36.229.108", dst_ip_address="10.36.229.46", controller_ip_address="10.36.229.108")
create_unidirectional_flow_json(src_ip_address="10.36.229.108", dst_ip_address="10.36.229.46", mac_addresses_map=mac_addresses_map)
create_rfc_2544_throuput_json(src_ip_address="10.36.229.108", dst_ip_address="10.36.229.46", mac_addresses_map=mac_addresses_map)
run_rfc_test_for_sanity()
