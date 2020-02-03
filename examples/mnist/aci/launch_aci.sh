#!/usr/bin/env bash
source /etc/azcreds/afscreds.sh
/etc/azcreds/azlogin.sh
jupyter nbconverter --to script $(1).ipynb
azcopy "aci_spec.yaml" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist/aci_spec.yaml?$SAS_TOKEN"
azcopy "$(1).py" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist/$(1).py?$SAS_TOKEN"
az container create -g $ACI_PERS_RESOURCE_GROUP --file aci_spec.yaml
azcopy "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist?$SAS_TOKEN" ./output --recursively
