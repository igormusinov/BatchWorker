import os
import logging
import argparse
from pathlib import Path

import re
import yaml

import uuid
import datetime
import subprocess

logger = logging.getLogger(__name__)

with open("/etc/azcreds/afscreds.sh", 'r') as f:
    envs = re.findall(r'(\w+)="(.*)"', f.read())
    for e, v in envs:
        os.environ[e] = v
USER_CLUSTER_NAME = os.environ["USER_CLUSTER_NAME"]
ACI_PERS_RESOURCE_GROUP = os.environ["ACI_PERS_RESOURCE_GROUP"]
ACI_PERS_STORAGE_ACCOUNT_NAME = os.environ["ACI_PERS_STORAGE_ACCOUNT_NAME"]
ACI_PERS_SHARE_NAME = os.environ["ACI_PERS_SHARE_NAME"]
SAS_TOKEN = os.environ["SAS_TOKEN"]


def gen_tag(user: str) -> str:
    time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{user}-{time}-{str(uuid.uuid4())[:2]}"


def check_file(path: Path) -> bool:
    if os.path.isfile(path):
        return True
    else:
        logging.exception(f" No file {path} ")
        raise


def proc_config(config: Path) -> (Path, dict):
    with open(config, 'r') as f:
        data = f.read()
        envs_list = re.findall(r'\$(\w+)', data)
        for e in envs_list:
            r = re.compile(f'\${e}')
            data = re.sub(r, os.environ[e], data)

    _config_spec = yaml.safe_load(data)
    _config = config.parent / f"_{config.name}"
    with open(_config, 'w') as f:
        yaml.dump(_config_spec, f)
    return _config, _config_spec


def console_command(cmd: list, timeout: int = 10000, *args, **kwargs) -> (str, int):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True, *args, **kwargs)

    log = ""
    start = datetime.datetime.now()
    while (datetime.datetime.now() - start).seconds < timeout:
        output = process.stdout.readline()
        log += output
        print(output.strip())
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                log += output
                print(output.strip())
            break
    return log, return_code


def aci_run(script: Path, config: Path):
    try:
        console_command(["az", "account", "show"])
    except Exception as exp:
        logging.error(
            f"Launch /etc/azcreds/azlogin.sh or login to your Azure account `az login`")
        console_command(["/bin/bash", "-c", "/etc/azcreds/azlogin.sh"])

    EXPERIMENT_FOLDER = gen_tag(USER_CLUSTER_NAME)
    os.environ["EXPERIMENT_FOLDER"] = EXPERIMENT_FOLDER
    os.environ["RESOURCE_NAME"] = EXPERIMENT_FOLDER
    _config, _config_spec = proc_config(config)
    group_name = f"{_config_spec['name']}"

    STORAGE_URI = "https://{}.file.core.windows.net/{}/{}/{}?{}".format(
        ACI_PERS_STORAGE_ACCOUNT_NAME,
        ACI_PERS_SHARE_NAME,
        EXPERIMENT_FOLDER,
        "{}",
        SAS_TOKEN)
    console_command(["azcopy", "cp", str(_config), STORAGE_URI.format(_config.name)])
    console_command(["azcopy", "cp", str(script), STORAGE_URI.format(script.name)])

    console_command(
        ["az", "container", "create", "-g", ACI_PERS_RESOURCE_GROUP, "--file",
         str(_config)])
    console_command(
        ["az", "container", "logs", "--follow", "-g", ACI_PERS_RESOURCE_GROUP, "-n",
         group_name])

    console_command(["azcopy", "cp",
                     STORAGE_URI.format('*'), f"./{EXPERIMENT_FOLDER}",
                     "--recursive=true"])
    console_command(["az", "container", "delete", "-g", ACI_PERS_RESOURCE_GROUP, "-n",
                     group_name, "-y"])

    return 0


def aks_run(script: Path, config: Path):
    try:
        console_command(["az", "account", "show"])
    except Exception as exp:
        logging.error(
            f"Launch /etc/azcreds/azlogin.sh or login to your Azure account `az login`")
        console_command(["/bin/bash", "-c", "/etc/azcreds/azlogin.sh"])

    EXPERIMENT_FOLDER = gen_tag(USER_CLUSTER_NAME)
    os.environ["EXPERIMENT_FOLDER"] = EXPERIMENT_FOLDER
    os.environ["RESOURCE_NAME"] = EXPERIMENT_FOLDER
    _config, _config_spec = proc_config(config)
    job_name = f"{_config_spec['name']}"

    STORAGE_URI = "https://{}.file.core.windows.net/{}/{}/{}?{}".format(
        ACI_PERS_STORAGE_ACCOUNT_NAME,
        ACI_PERS_SHARE_NAME,
        EXPERIMENT_FOLDER,
        "{}",
        SAS_TOKEN)
    console_command(["azcopy", "cp", str(_config), STORAGE_URI.format(_config.name)])
    console_command(["azcopy", "cp", str(script), STORAGE_URI.format(script.name)])

    console_command(
        ["kubectl", "--kubeconfig=/etc/azcreds/kubeconfig.users", "apply", "-f",
         _config])
    pod_name, _ = console_command(
        ["kubectl", "--kubeconfig=/etc/azcreds/kubeconfig.users", "get", "pods", "|"
                                                                                 "grep",
         job_name, "|", "awk", "'{print $1}'"])
    console_command(
        ["kubectl", "--kubeconfig=/etc/azcreds/kubeconfig.users", "logs", "pod",
         pod_name, "-f"])

    console_command(["azcopy", "cp",
                     STORAGE_URI.format('*'), f"./{EXPERIMENT_FOLDER}",
                     "--recursive=true"])
    console_command(
        ["kubectl", "--kubeconfig=/etc/azcreds/kubeconfig.users", "delete", "-f",
         _config])

    return 0


def slurm_run():
    pass


def main():
    parser = argparse.ArgumentParser(description="Run job on the ACI")
    parser.add_argument('--notebook', help='Specify jupyter notebook file',
                        required=True)
    parser.add_argument('--config', help='Specify config file', required=True)
    parser.add_argument('--cluster', help='Choose cluster', default="ACI")
    parser.add_argument('--locac_data_folder', help='Specify your local data folder')
    parser.add_argument('--azure_data_uri',
                        help='Specify your data in your azure storage')
    args = parser.parse_args()

    check_file(args.notebook)
    check_file(args.config)

    notebook = Path(args.notebook)
    os.environ["PYSCRIPT"] = notebook.name.replace(".ipynb", "")
    console_command(["jupyter", "nbconvert", "--to script", str(notebook)])
    script = notebook.parent / notebook.name.replace("ipynb", "py")

    if args.cluster == "ACI":
        aci_run(script, Path(args.config))
    else:
        logging.error(f"Method {args.cluster} is not realised :(")
        raise
        return 2


if __name__ == '__main__':
    main()
