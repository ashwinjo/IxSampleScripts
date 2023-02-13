import paramiko
import time


def get_linux_chassis_information_from_cli(chassis_ip, username, password):
    # Create an instance of the SSH client
    ssh = paramiko.SSHClient()

    # Automatically add the server's SSH key (for the first time only)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect(chassis_ip, username=username, password=password)
    chan = ssh.invoke_shell(width=500)

    # Ssh and wait for the password prompt.
    send_command_and_print_info(chan, 'enter chassis\n')

    print("\n******************* Chassis Version Infromation Screen ***********************\n")
    send_command_and_print_info(chan, 'show welcome-screen\n')

    print("\n******************* Chassis Info Fetch Date ***********************\n")
    send_command_and_print_info(chan, 'show date\n')

    print("\n******************* Chassis Uptime ***********************\n")
    send_command_and_print_info(chan, 'show uptime\n')

    print("\n******************* Chassis Topology ***********************\n")
    send_command_and_print_info(chan, 'show topology\n')

    print("\n******************* License Details ***********************\n")
    send_command_and_print_info(chan, 'show licenses\n')

    # print("\n******************* Collect Logs ***********************\n")
    # chan.send('collect-logs\n')
    # resp  = ''
    # while not resp.endswith('# '):
    #     resp = chan.recv(9999)
    #     resp = str(resp, 'UTF-8')
    #     print(resp)

    # Close the connection
    ssh.close()


def send_command_and_print_info(chan, command):
    chan.send(command)
    time.sleep(5)
    resp = ''
    while not resp.endswith('# '):
        resp = chan.recv(9999)
        resp = str(resp, 'UTF-8')
        if "enter chassis" not in command:
            print(resp)
