Deployment of ixia-c/KENG on Azure Public Cloud

Azure Infrastructure
===

1) Spin up 2 Ubuntu VM's in same VNET with 2 subnets
   > Management Subnet (10.0.0.0/24)
   > Test Subnet (10.0.1.0/24)
   
2) Create private interfaces inside Test Subnet
   > testInferface1 (10.0.1.4)
   > testInterface2 (10.0.1.5)
   
3) Associate Public IPs with Mgmt Subnet Interfaces / Use a bastion to communicate with these VM's

<img width="1723" alt="image" src="https://github.com/ashwinjo/IxSampleScripts/assets/120066169/9bd87417-ec2d-4686-b8d5-f6a154a2327c">


Setup Azure VM's
===

> sudo su
> **Install Docker (https://docs.docker.com/engine/install/ubuntu/)**
# Add Docker's official GPG key:
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

# Add the repository to Apt sources:
```bash
 echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin python3-pip net-tools
```

> Pull Traffic Engine and Controller Images on VM"s. You will need Traffic Engines on both VM's but controller on single VM. You can also host controller on completely different 3rd VM in
> same subnet
```bash
docker pull ghcr.io/open-traffic-generator/ixia-c-controller:latest
docker pull ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
```

> Run Traffic Engines and Controllers
* Identify what is your test interface called. In my case it is "eth1"
  ```bash
  docker run -d --name Ixia-c-Traffic-Engine-1 --network=host --privileged -e ARG_IFACE_LIST=virtual@af_packet,**eth1** -e OPT_NO_HUGEPAGES=Yes -e OPT_LISTEN_PORT=**5551**  ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
 
  docker run -d --name Ixia-c-Controller --network=host \ ghcr.io/open-traffic-generator/ixia-c-controller:latest --accept-eula
  ```


> Lets Install test dependencies
```bash
* pip3 install snappi
* pip3 install pytest
```

Download file from 
```bash
https://github.com/ashwinjo/IxSampleScripts/blob/main/handyScripts/snappiTest.py.
```
onto the host
Run Test
===

> Go to the VM where you have controller.

```python
python3 snappiTest.py
```

<img width="1728" alt="Pasted Graphic 4" src="https://github.com/ashwinjo/IxSampleScripts/assets/120066169/77bebe07-974b-4552-904c-22ee086c8ee3">

You will see metrics updating as test runs. Here test only ran for 10 secs. You can further modify test to match your parameters.
