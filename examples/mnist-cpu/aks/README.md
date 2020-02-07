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
5. In the same console `./launch_aks.sh mnist` from this folder 
