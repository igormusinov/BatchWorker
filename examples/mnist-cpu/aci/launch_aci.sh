#!/usr/bin/env bash
source /etc/azcreds/afscreds.sh
/etc/azcreds/azlogin.sh
if test -f "$1.ipynb"; then
    jupyter nbconvert --to script $1.ipynb
    envsubst < aci_spec.yaml > _aci_spec.yaml
    azcopy cp "_aci_spec.yaml" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist/_aci_spec.yaml?$SAS_TOKEN"
    azcopy cp "$1.py" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist/$1.py?$SAS_TOKEN"
    az container create -g $ACI_PERS_RESOURCE_GROUP --file _aci_spec.yaml
    azcopy "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist?$SAS_TOKEN" ./output --recursively
    az container delete -g $ACI_PERS_RESOURCE_GROUP -n $USER-gpucontainergroup -y
fi