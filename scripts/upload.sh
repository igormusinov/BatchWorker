#!/bin/bash
#MartS 2020 admin.marts@gmail.com
source /etc/azcreds/afscreds.sh
#/etc/azcreds/azlogin.sh
if [ -z "${SAS_TOKEN}" ]; then
	echo "Please get your credentials first"
	exit 1
fi
if [ -z $1 ]; then
	echo -e  "Usage: ./upload.sh file/dir\r\nFile would be placed to ${ACI_PERS_SHARE_NAME}/$(whoami)/mnnist/ folder"
	exit 1
fi
azcopy cp --recursive  $1  "https://$ACI_PERS_STORAGE_ACCOUNT_NAME.file.core.windows.net/$ACI_PERS_SHARE_NAME/$(whoami)/mnist/?$SAS_TOKEN"
echo -e  "${ACI_PERS_SHARE_NAME}/$(whoami)/mnnist/\n"
