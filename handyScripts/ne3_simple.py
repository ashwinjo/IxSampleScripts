import requests

import json

import base64

 

# set up login parameters

ne2_ip = '10.36.158.21'

ne2_username = 'admin'

ne2_password = 'admin'

ne2_user_pass = ne2_username + ':' + ne2_password

base64_ne2_user_pass = base64.b64encode(ne2_user_pass.encode())

 

# login and get token for future commands

request_headers = {

'Authorization':'Basic ' + base64_ne2_user_pass.decode(),

'Content-Type':'application/json'

}

request_url = 'http://' + ne2_ip + '/api'

response = requests.get(request_url, headers = request_headers)

response_headers = response.headers

ne2_auth_token = response_headers['X-Auth-Token']

 

# set up header with token for login

request_url = 'http://' + ne2_ip + '/api/hw/Port/5'

request_headers = {

'Authorization':'Token ' + ne2_auth_token,

'Content-Type':'application/json'

}

 

# add a profle to filter on MAC address and delay 150ms

request_payload = '{"profiles": [ { "tag": "Port5-Profile1", "enabled": "true", "rules": [{"bitRange": "L2@6[7]+47","field": "Common::MAC::Source Address","value": "aaaaaaaaaaa","mask": "ffffffffffff"}],"ethernetDelay": { "delay": 150, "pdvMode": "NONE", "units": "MS", "enabled": "true" } } ] }'

response = requests.put(request_url, headers=request_headers, data=request_payload )

print(response)

print("profile 1 added")

 

# add a second profile with no filter or impairments

request_payload = '{"profiles": [ {}, { "tag": "Port5-Profile2", "enabled": "true" } ] }'

response = requests.put(request_url, headers=request_headers, data=request_payload )

print(response)

print("profile 2 added")
