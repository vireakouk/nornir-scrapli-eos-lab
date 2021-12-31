from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import send_config, send_commands
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--dry_run", dest="drill", action="store_true", help="This is a drill.")
parser.add_argument("--no_dry_run", dest="drill", action="store_false", help="This is not a drill.")
parser.set_defaults(drill=True)
args = parser.parse_args()

dry_run = args.drill



def deploy_base(task: Task) -> Result:
    r = task.run(task=template_file, 
                template="base.j2", 
                path="./templates")
                
    task.host["config"] = r.result

    task.run(task=send_config,
            name="Deploy base configuration on the device.",
            dry_run=False,
            config=task.host["config"])

    task.run(task=send_commands, 
            name="Show new config and copy running config to startup config.", 
            commands=["show run", "write memory"])

if __name__ == "__main__":
    nr = InitNornir(config_file="config.yml")
    r = nr.run(task=deploy_base)
    print_result(r)    