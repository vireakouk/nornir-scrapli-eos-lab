from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import send_config, send_commands
from utils import nornir_set_creds
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--dry_run", dest="drill", action="store_true", default=False, help="This is a drill.")
args = parser.parse_args()

isDryrun = args.drill


def deploy_base(task: Task) -> Result:
    r = task.run(task=template_file, 
                template="base.j2", 
                path="./templates")
                
    task.host["config"] = r.result

    task.run(task=send_config,
            name="Deploy base configuration on the device.",
            dry_run=isDryrun,
            config=task.host["config"])

    task.run(task=send_commands, 
            name="Show new config and copy running config to startup config.", 
            commands=["show run", "write memory"])

if __name__ == "__main__":
    nr = InitNornir(config_file="config.yml", core={"raise_on_error": True})
    nornir_set_creds(nr)
    r = nr.run(task=deploy_base)
    print_result(r)    