# BatchWorker
Batch worker for slurm, kubernetes, ACI

## Install

0. Create symlinks for launch_aci.sh, launch_aks.sh
```bash
sudo ln -s /usr/bin/local/launch_aci.sh ./bin/launch_aci.sh
sudo ln -s /usr/bin/local/launch_aks.sh ./bin/launch_aks.sh
```
1. Get creds afscreds.sh and azlogin.sh from admins
2. Create folder /etc/azcreds and put these 2 files with +x

```bash
sudo mkdir /etc/azcreds
unzip archive && sudo cp afscreds.sh azlogin.sh /etc/azcreds/
sudo chmod +x /etc/azcreds/*.sh
```

3. Install az (https://docs.microsoft.com/ru-ru/cli/azure/install-azure-cli?view=azure-cli-latest) 
and azcopy (https://docs.microsoft.com/ru-ru/azure/storage/common/storage-use-azcopy-v10)
4. Login to the Azure account `/etc/azcreds/azlogin.sh`


## ACI

5. In the same console `launch_aci.sh mnist` from the folder with mnist.ipynb

## AKS (or Kubernetes cluster)

5. In the same console `launch_aks.sh mnist` from the folder with mnist.ipynb

## Slurm [deprecated]