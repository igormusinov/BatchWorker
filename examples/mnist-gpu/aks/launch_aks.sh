#!/usr/bin/env bash
source /etc/azcreds/afscreds.sh
if test -f "$1.ipynb"; then
    export PYSCRIPT=$1
    jupyter nbconvert --to script $1.ipynb
    export EXPERIMENT_FOLDER=$USER_CLUSTER_NAME-$(date +"%F-%H-%M-%S")
    export RESOURCE_NAME=$EXPERIMENT_FOLDER
    envsubst < aks_spec.yaml > _aks_spec.yaml
    azcopy cp "_aks_spec.yaml" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/_aks_spec.yaml?$SAS_TOKEN"
    azcopy cp "$1.py" "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/$1.py?$SAS_TOKEN"
    kubectl --kubeconfig=/etc/azcreds/kubeconfig.users apply -f _aks_spec.yaml
until kubectl --kubeconfig=/etc/azcreds/kubeconfig.users get jobs $RESOURCE_NAME -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}' | grep True ; do sleep 1 ; done
    azcopy cp  "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$EXPERIMENT_FOLDER/*?$SAS_TOKEN" ./$EXPERIMENT_FOLDER --recursive=true
    kubectl --kubeconfig=/etc/azcreds/kubeconfig.users delete -f _aks_spec.yaml
else
    echo "No $1.ipynb"
fi
