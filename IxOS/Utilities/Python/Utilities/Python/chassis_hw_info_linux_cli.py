import paramiko
import time

def get_linux_chassis_information(chassis_ip, username, password):
    # Create an instance of the SSH client
    ssh = paramiko.SSHClient()

    # Automatically add the server's SSH key (for the first time only)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect(chassis_ip, username=username, password=password)
    chan = ssh.invoke_shell(width=500)

    # Ssh and wait for the password prompt.
    chan.send('enter chassis\n')
    resp = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        
    print("\n******************* Chassis Info Fetch Date ***********************\n")
    chan.send('show date\n')
    resp  = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        print(resp)
    
        
    print("\n******************* Chassis Uptime ***********************\n")
    chan.send('show uptime\n')
    resp  = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        print(resp)
    
        
    print("\n******************* Chassis Topology ***********************\n")
    chan.send('show topology\n')
    resp  = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        print(resp)
    
        
    print("\n******************* License Details ***********************\n")
    chan.send('show licenses\n')
    resp  = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        print(resp)

    # Close the connection
    ssh.close()
    


CHASSIS_LIST = [{"ip": "X.X.X.X", "username": "XXX", "password": "XXX"}]

if __name__ == "__main__":
    for chassis in CHASSIS_LIST:
        get_linux_chassis_information(chassis["ip"], 
                                      chassis["username"], 
                                      chassis["password"])
