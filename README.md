# nornir-scrapli-eos-lab
Network automation lab using nornir, scrapli, and containerlab with Arista EOS.

# Objectives
1. Deploy base configs to 4xArista devices via scrapli
2. Deploy interface configs to 4xArista devices via scrapli
3. Deploy underlay BGP configs to 4xArista devices via scrapli

# Tools
1. Containerlab (https://containerlab.srlinux.dev/)
2. nornir (https://github.com/nornir-automation/nornir)
3. nornir_utils (https://github.com/nornir-automation/nornir_utils)
4. nornir-jinja2 (https://github.com/nornir-automation/nornir_jinja2)
5. nornir-scrapli (https://github.com/scrapli/nornir_scrapli)

# My environment
- Ubuntu Server 20.04 LTS x86_64 with 32GB RAM running in VirtualBox (Windows 10 Pro). This lab only consumes a bit less than 4GB of RAM.
- Containerlab version 0.16.2 (any later version should do)
- Docker 20.10.8

# Containerlab
Containerlab provides a CLI for orchestrating and managing container-based networking labs. Follow the instruction in the containerlab website to install it for Linux. 
https://containerlab.srlinux.dev/install/

# Arista ceos images
Arista is kind enough to provide docker images of their EOS routing platform for learning and testing purpose via their website together with the instruction to get it to work with Docker. 
I'm using ceosimage:4.26.1F

# Setup
Clone the repo:
```
git clone https://github.com/vireakouk/nornir-scrapli-eos-lab.git
```
Create a Python3 virtual environment in the project directory:
```
python3 -m venv env
```
Activate virtual environment:
```
source env/bin/activate
```
and install the following:
```
pip install nornir
pip install nornir-scrapli
pip install nornir_utils
pip install nornir-jinja2
```
or use requirements.txt
```
pip install -r requirements.txt
```
# Spinning up the lab
```
cd containerlab/
sudo containerlab deploy -t eos.clab.yml
```
(use "sudo containerlab deploy -t eos.clab.yml --reconfigure" to do a clean boot if you run it not for the first time.)

Wait for a minute or two for all devices to boot up and make sure you can ssh to each device using admin/admin credential. Scrapli in this case use ssh port 22 as transport.

# Deploy base config (deploy_baseconfig.py)
```
cd nornir-scrapli-eos-lab/
python deploy_baseconfig.py
```
This simple script achieves the following:
1. create a user account,
2. enable ip routing,
3. config loopback0 interface with ipv4 and ipv6,  
4. remove all configs from other interfaces and shut them down (except loopback0 and mgmt)

It does those by:
1. Generate a temporary config per device by filling the template file templates/base.j2 with the hosts variables in the inventory files (hosts.yml, groups.yml, and defaults.yml)
```
r = task.run(task=template_file, 
                template="base.j2", 
                path="./templates")
```
2. Store the resultant config to each specific host variable dictionary with an abitary key "config" :
```
task.host["config"] = r.result
```
3. Send the config to device using scrapli send_config method:
```
task.run(task=send_config,
            name="Deploy base configuration on the device.",
            dry_run=False,
            config=task.host["config"])
```
4. Display the new changed config using scrapli send_command method:
```
task.run(task=send_command, 
            name="Show new config", 
            command="show run")
```
# Deploy interface configs (deploy_interfaces.py)
```
cd nornir-scrapli-eos-lab/
python deploy_interfaces.py
```
This simple script achieves the following:
1. config interfaces with description, ipv4, ipv6, disable switchport  
2. enable the interface with "no shutdown"

It does those by:
1. Generate a temporary config per device by filling the template file templates/interfaces.j2 by looping through interface values in hosts variables in the inventory files (hosts.yml)
```
r = task.run(task=template_file, 
                template="interfaces.j2", 
                path="./templates")
```
2. Store the resultant config to each specific host variable dictionary with an abitary key "config" :
```
task.host["config"] = r.result
```
3. Send the config to device using scrapli send_config method:
```
task.run(task=send_config, 
            name="Configuring interfaces!", 
            dry_run=False,
            config=task.host["config"])
```
4. Display the new changed config using scrapli send_command method:
```
task.run(task=send_command, 
            name="Show new config", 
            command="show run")
```
# Verify results of interface configs 
After the deployment, if there is no error, you should be able to ping adjacent interfaces. If you can't, check the nornir.log for clues on the errors.

# Deploy underlay BGP configs (deploy_underlay.py)
Follow the same concepts as the two previous tasks but using "templates/underlay.j2" instead.

# Verify results of underlay configs 
After the deployment, if there is no error, you should be all bgp adjacency established.
```
spine1>show ip bgp summary
BGP summary information for VRF default
Router identifier 1.1.1.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.1.1.1         4 65001              3         3    0    0 00:00:02 Estab   0      0
  10.1.1.3         4 65002              3         3    0    0 00:00:02 Estab   0      0
spine1>
```
```
leaf1#show ip bgp summary
BGP summary information for VRF default
Router identifier 1.1.1.3, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.1.1.0         4 65000              3         3    0    0 00:00:16 Estab   0      0
  10.1.1.4         4 65000              3         3    0    0 00:00:16 Estab   0      0
leaf1#
```

# Extension of script functionality 
The template is standard jinja2 template which you can add more parameters to the base or interface configs. For example in base config, we can add further template for aaa, logging, ntp, logging..etc.

# More tasks 
(learning in progress)
