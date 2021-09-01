from logging import ERROR
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import send_commands, send_config

def deploy_int(task: Task, data: dict) -> Result:
    task.host["vxlan"] = data
    r = task.run(task=template_file, 
                template="l2vxlan.j2",
                path="./templates")
    task.host["config"] = r.result


    task.run(task=send_config, 
            name="Provisioning L2 VXLAN!", 
            dry_run=False,
            config=task.host["config"])
    
    task.run(task=send_commands, 
            name="Show new config and copy running config to startup config.", 
            commands=["show run", "write memory"])

def get_input() -> dict:
    print("*"*60)
    print("* This tool will provision L2 VxLAN circuit in leaf nodes. *")
    print("*"*60)
    data = {}
    data["vlan_id"] = input("Enter the vlan ID (ex: 10): ")
    data["vlan_name"] = input("Enter the vlan name (ex: CUST-ABC): ")
    data["vni"] = input("Enter the vni (ex: 10010): ")
    data["a_end"] = input("Enter the A-end switch name: ")
    data["b_end"] = input("Enter the B-end switch name: ")
    
    return data


if __name__ == "__main__":
    user_input = get_input()
    nr = InitNornir(config_file="config.yml")
    try:
        nr = nr.filter(F(switchname=user_input["a_end"]) | F(switchname=user_input["b_end"]))
        r = nr.run(task=deploy_int, data=user_input)
        print_result(r)
    except KeyError as e:
        print(f"Could not find the switch: {e}")
    