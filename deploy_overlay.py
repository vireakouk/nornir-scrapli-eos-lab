from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import send_commands, send_config

def deploy_over(task: Task) -> Result:
    r = task.run(task=template_file, 
                template="overlay.j2",
                path="./templates")
    task.host["config"] = r.result

    task.run(task=send_config, 
            name="Configuring overlay!", 
            dry_run=False,
            config=task.host["config"])
    
    task.run(task=send_commands, 
            name="Show new config and copy running config to startup config.", 
            commands=["show run", "write memory"])

if __name__ == "__main__":
    nr = InitNornir(config_file="config.yml")
    r = nr.run(task=deploy_over)
    print_result(r)
