#!/bin/bash
#
# MIT License
#
# (C) Copyright 2023-2024 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

# This script is called during the Docker image build.
# It isolates the zypper operations, some of which require artifactory authentication,
# and scrubs the zypper environment after the necessary operations are completed.

# Preconditions:
# 1. Following variables have been set in the Dockerfile: SP ARCH CSM_SSH_KEYS_VERSION
# 2. zypper-refresh-patch-clean.sh script has also been copied into the current directory

# Based in part on: https://github.com/Cray-HPE/uai-images/blob/main/uai-images/broker_uai/zypper.sh

set -e +xv
trap "rm -rf /root/.zypp" EXIT

# Get artifactory credentials and use them to set the csm-rpms stable sles15sp$SP repository URI
ARTIFACTORY_USERNAME=$(test -f /run/secrets/ARTIFACTORY_READONLY_USER && cat /run/secrets/ARTIFACTORY_READONLY_USER)
ARTIFACTORY_PASSWORD=$(test -f /run/secrets/ARTIFACTORY_READONLY_TOKEN && cat /run/secrets/ARTIFACTORY_READONLY_TOKEN)
CREDS=${ARTIFACTORY_USERNAME:-}
# Append ":<password>" to credentials variable, if a password is set
[[ -z ${ARTIFACTORY_PASSWORD} ]] || CREDS="${CREDS}:${ARTIFACTORY_PASSWORD}"
CSM_SLES_REPO_URL="https://${CREDS}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp${SP}?auth=basic"
CSM_NOOS_REPO_URL="https://${CREDS}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/noos?auth=basic"
SLES_MIRROR_URL="https://${CREDS}@artifactory.algol60.net/artifactory/sles-mirror"
SLES_PRODUCTS_URL="${SLES_MIRROR_URL}/Products"
SLES_UPDATES_URL="${SLES_MIRROR_URL}/Updates"

function add_zypper_repos {
    local label
    label=$1
    zypper --non-interactive ar "${SLES_PRODUCTS_URL}/SLE-${label}/15-SP${SP}/${ARCH}/product/?auth=basic" "sles15sp${SP}-${label}-product"
    zypper --non-interactive ar "${SLES_UPDATES_URL}/SLE-${label}/15-SP${SP}/${ARCH}/update/?auth=basic" "sles15sp${SP}-${label}-update"
}

if [[ ${SP} -lt 5 ]]; then
    # The mirrors for these earlier SLES SPs are no longer available
    echo "ERROR: SP == $SP, but must be 5+" >&2
    exit 1
fi

zypper --non-interactive rr --all
zypper --non-interactive clean -a
for MODULE in Basesystem Certifications Containers Desktop-Applications Development-Tools HPC Legacy Packagehub-Subpackages \
              Public-Cloud Python3 Server-Applications Web-Scripting
do
    add_zypper_repos "Module-${MODULE}"
done
PRODUCTS="SLES WE"
if [[ ${SP} -lt 6 ]]; then
    # HPC is deprecated in SP6, but we want to include it for previous SPs
    PRODUCTS="${PRODUCTS} HPC"
fi
for PRODUCT in $PRODUCTS; do
    add_zypper_repos "Product-${PRODUCT}"
done
zypper --non-interactive ar --no-gpgcheck "${CSM_SLES_REPO_URL}" csm-sles
zypper --non-interactive ar --no-gpgcheck "${CSM_NOOS_REPO_URL}" csm-noos
zypper --non-interactive --gpg-auto-import-keys refresh
zypper --non-interactive in -f --no-confirm csm-ssh-keys-roles-${CSM_SSH_KEYS_VERSION}
# Lock the version of csm-ssh-keys-roles, just to be certain it is not upgraded inadvertently somehow later
zypper --non-interactive al csm-ssh-keys-roles
# Apply security patches (this script also does a zypper clean)
./zypper-refresh-patch-clean.sh
# Remove all repos & scrub the zypper directory 
zypper --non-interactive rr --all
rm -f /etc/zypp/repos.d/*
