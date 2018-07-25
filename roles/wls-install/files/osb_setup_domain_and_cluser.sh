#!/bin/bash

set -e

SCRIPT=$(readlink -f $0)
SCRIPT_PATH=$(dirname $SCRIPT)

source ${SCRIPT_PATH}/osb_set_environment_variables.sh

create_domain_and_cluster() {
	${FUSION_MIDDLEWARE_HOME}/common/bin/wlst.sh -loadProperties ${SCRIPT_PATH}/../config/osb_environment.properties ${SCRIPT_PATH}/osb_setup_domain_and_cluser.py
}

change_memory_settings() {

	echo '[INFO] Change DERBY flag'
	sed -i -e '/DERBY_FLAG="true"/ s:DERBY_FLAG="true":DERBY_FLAG="false":' ${DOMAIN_CONFIGURATION_HOME}/bin/setDomainEnv.sh

}

create_domain_and_cluster

change_memory_settings
