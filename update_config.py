from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_configs_from_file, send_commands
from utils import nornir_set_creds
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--dry_run", dest="drill", action="store_true", default=False, help="This is a drill.")
args = parser.parse_args()

isDryrun = args.drill


def update_cfg(task: Task) -> Result:

    task.run(task=send_configs_from_file,
            name="Update config configuration on the device.",
            dry_run=isDryrun,
            file=f"./snapshots/configs/{task.host}.cfg")

    task.run(task=send_commands, 
            name="Show new config and copy running config to startup config.", 
            commands=["show run", "write memory"])

if __name__ == "__main__":
    nr = InitNornir(config_file="config.yml", core={"raise_on_error": True})
    nornir_set_creds(nr)
    r = nr.run(task=update_cfg, raise_on_error=True)
    print_result(r)    