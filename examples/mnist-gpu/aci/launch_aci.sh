#!/usr/bin/env bash
source /etc/azcreds/afscreds.sh
# /etc/azcreds/azlogin.sh
if test -f "$1.ipynb"; then
    jupyter nbconvert --to script $1.ipynb
    export EXPERIMENT_FOLDER=$USER_CLUSTER_NAME-$(date +"%F-%H-%M-%S")
    export RESOURCE_NAME=$EXPERIMENT_FOLDER
    envsubst < aci_spec.yaml > _aci_spec.yaml

    azcopy cp "_aci_spec.yaml" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/_aci_spec.yaml?$SAS_TOKEN"
    azcopy cp "$1.py" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/$1.py?$SAS_TOKEN"
    az container create -g $ACI_PERS_RESOURCE_GROUP --file _aci_spec.yaml
    az container attach -g $ACI_PERS_RESOURCE_GROUP -n $RESOURCE_NAME
    azcopy cp  "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/*?$SAS_TOKEN" ./$EXPERIMENT_FOLDER --recursive=true
    az container delete -g $ACI_PERS_RESOURCE_GROUP -n $RESOURCE_NAME -y
else
    echo "No $1.ipynb"
fi