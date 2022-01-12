from logging import config
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import cfg_get_config
from utils import nornir_set_creds


def backup_cfg(task: Task) -> Result:
    r = task.run(
            task=cfg_get_config,
            source = "running",
            name="Get running config from each host")

    task.host["config"] = r.result
    print_result(r)
    
    with open (f"./snapshots/configs/{task.host}.txt", "w", encoding="utf-8") as file:
        file.write(task.host["config"])


if __name__ == "__main__":
    nr = InitNornir(config_file="config.yml", core={"raise_on_error": True})
    nornir_set_creds(nr)
    r = nr.run(task=backup_cfg)