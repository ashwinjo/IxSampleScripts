
import paramiko
import time
import re
import json


class SshCommandsWrapper:
    def __init__(self, chassis_ip, username, password):
        self.chassis_ip = chassis_ip
        self.username = username
        self.password = password

    def do_license_check_operation(self, operation="get"):
        data = {}
        # Create an instance of the SSH client
        ssh = paramiko.SSHClient()

        # Automatically add the server's SSH key (for the first time only)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(self.chassis_ip, username=self.username, password=self.password)
        chan = ssh.invoke_shell(width=500)

        # Ssh and wait for the password prompt.
        self.send_command_and_print_info(chan, 'enter chassis\n')

        if operation.lower() == "get":
            license_check = self.send_command_and_print_info(chan, 'show welcome-screen\n')
            raw = ''.join(license_check)
            clean = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', raw)
            data = {
                match.group(1).strip(): match.group(2).strip()
                for match in re.finditer(r'\|\s*(.+?)\s*:\s*(.+?)\s*\|', clean)
            }
            return data

        if operation.lower() in ["enable", "disable"]:
            license_check = self.send_command_and_print_info(chan, f'set license-check {operation.lower()}\n')
            return license_check[0].split("\r\n")[1].replace('\x1b[39m', '').replace('\x1b[33m', '')

        # Close the connection
        ssh.close()
        return data

    def send_command_and_print_info(self, chan, command):
        chan.send(command)
        time.sleep(5)
        resp = ''
        rs = []
        while not resp.endswith('# '):
            resp = chan.recv(9999)
            resp = str(resp, 'UTF-8')
            if "enter chassis" not in command:
                rs.append(resp)
        return rs


if __name__ == "__main__":
    wrapper = SshCommandsWrapper(
        chassis_ip="10.36.236.121",
        username="admin",
        password="Kimchi123Kimchi123!",
    )
    result = wrapper.do_license_check_operation(operation="get")
    print(json.dumps(result, indent=2))
""""
Output:
python3 ssh_commands_wrapper.py
{
  "Management IPv4": "10.36.236.121",
  "Management IPv6": "2001::1",
  "Active IxOS Version": "26.0.1+2600.20",
  "IxNetwork Protocols Version": "26.0.2601.3",
  "LicenseServerPlus Version": "5.70.1.2",
  "Chassis status": "READY"
}
"""
