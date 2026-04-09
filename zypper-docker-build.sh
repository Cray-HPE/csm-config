#!/bin/bash
#
# MIT License
#
# (C) Copyright 2023-2026 Hewlett Packard Enterprise Development LP
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

# Usage:
# zypper-docker-build.sh [<package1> [<package2> ...]]
#                        [--lock <package x> [<package y> ...]]
#                        [--remove <package a> [<package b> ...]]
# 1. Adds the repos
# 2. Installs the specified packages (if any)
# 3. Removes the specified packages (if any)
# 4. Locks the specified packages (if any)
# 5. Applies curl workaround, if necessary
# 6. Applies security patches (if any)
# 7. Removes repos

# Based in part on: https://github.com/Cray-HPE/uai-images/blob/main/uai-images/broker_uai/zypper.sh

set -e +xv
trap "rm -rf /root/.zypp" EXIT

INSTALL_LIST=()
LOCK_LIST=()
REMOVE_LIST=()
# First handle packages to be installed, since they have to be listed first
# if they are present

# Consume all arguments until we reach the end of the
# arguments or until we hit an argument beginning with --
while [[ $# -gt 0 && ${1:0:2} != -- ]]; do
    INSTALL_LIST+=( "$1" )
    shift
done

# Now process the remaining arguments, if any
while [[ $# -gt 0 ]]; do
    op="$1"
    shift
    case "$op" in
        "--lock")
            # Consume all subsequent arguments until we reach the end of the
            # arguments or until we hit an argument beginning with --
            while [[ $# -gt 0 && ${1:0:2} != -- ]]; do
                LOCK_LIST+=( "$1" )
                shift
            done
            ;;
        "--remove")
            # Consume all subsequent arguments until we reach the end of the
            # arguments or until we hit an argument beginning with --
            while [[ $# -gt 0 && ${1:0:2} != -- ]]; do
                REMOVE_LIST+=( "$1" )
                shift
            done
            ;;
        *)
            echo "USAGE ERROR: Invalid argument: $op" 1>&2
            exit 1
            ;;
    esac
done

# Get artifactory credentials and use them to set the repository URLs
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

function run_cmd_retry
{
    local num rc
    num=0
    while [[ $num -lt 5 ]]; do
        [[ $num -eq 0 ]] || sleep 5
        echo "# $*"
        "$@" && return 0 || rc=$?
        echo "Command failed with rc $rc"
        let num+=1
    done
    echo "Command failed even after retries"
    return $rc
}

function add_zypper_product_repo {
    local label repo_sp
    label=$1
    if [[ $# -eq 2 ]]; then
        repo_sp=$2
    else
        repo_sp=${SP}
    fi
    run_cmd_retry zypper --non-interactive ar "${SLES_PRODUCTS_URL}/SLE-${label}/15-SP${repo_sp}/${ARCH}/product/?auth=basic" "sles15sp${repo_sp}-${label}-product"
}

function add_zypper_update_repo {
    local label repo_sp
    label=$1
    if [[ $# -eq 2 ]]; then
        repo_sp=$2
    else
        repo_sp=${SP}
    fi
    run_cmd_retry zypper --non-interactive ar "${SLES_UPDATES_URL}/SLE-${label}/15-SP${repo_sp}/${ARCH}/update/?auth=basic" "sles15sp${repo_sp}-${label}-update"
}

function add_zypper_repos {
    local label repo_sp
    label=$1
    if [[ $# -eq 2 ]]; then
        repo_sp=$2
    else
        repo_sp=${SP}
    fi
    add_zypper_product_repo "${label}" "${repo_sp}"
    add_zypper_update_repo "${label}" "${repo_sp}"
}

function remove_zypper_repos {
    local label repo_sp
    label=$1
    if [[ $# -eq 2 ]]; then
        repo_sp=$2
    else
        repo_sp=${SP}
    fi
    run_cmd_retry zypper --non-interactive rr "sles15sp${repo_sp}-${label}-product"
    run_cmd_retry zypper --non-interactive rr "sles15sp${repo_sp}-${label}-update"
}

if [[ ${SP} -lt 5 ]]; then
    # The mirrors for these earlier SLES SPs are no longer available
    echo "ERROR: SP == $SP, but must be 5+" >&2
    exit 1
fi

run_cmd_retry zypper --non-interactive rr --all
run_cmd_retry zypper --non-interactive clean -a

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

# SP < 7 also have LTSS update repos
# Once SP 7 goes LTSS, this should be updated accordingly
if [[ $SP -lt 7 ]]; then
    add_zypper_update_repo Product-SLES "${SP}-LTSS"
fi

run_cmd_retry zypper --non-interactive ar --no-gpgcheck "${CSM_SLES_REPO_URL}" csm-sles
run_cmd_retry zypper --non-interactive ar --no-gpgcheck "${CSM_NOOS_REPO_URL}" csm-noos
run_cmd_retry zypper --non-interactive --gpg-auto-import-keys refresh

if [[ ${#INSTALL_LIST[@]} -gt 0 ]]; then
    run_cmd_retry zypper --non-interactive in -f --no-confirm "${INSTALL_LIST[@]}"
fi

if [[ ${#REMOVE_LIST[@]} -gt 0 ]]; then
    run_cmd_retry zypper --non-interactive rm --no-confirm "${REMOVE_LIST[@]}"
fi

if [[ ${#LOCK_LIST[@]} -gt 0 ]]; then
    run_cmd_retry zypper --non-interactive al "${LOCK_LIST[@]}"
fi

#############################################################################
# curl bug workaround
#############################################################################

# There is a bug in curl that breaks some operations
# https://github.com/curl/curl/issues/13229
# We know that it is not yet present in curl v8.5 and is fixed in v8.8.
# The current SP6 repos don't have a version without this problem. So we add
# an SP5 repo to pull in a good version of it

function apply_curl_bug_workaround
{
    local S
    # First try to install a newer version, where the bug is fixed, using
    # just our current repos
    if ! zypper --non-interactive in --force-resolution --no-confirm --no-recommends 'curl>=8.8' ; then

        # Failing that, add in the earlier repos

        # Add in the earlier repos (SP5+)
        S=5
        while [[ $S -lt $SP ]]; do
            add_zypper_repos Module-Basesystem "$S"
            let S+=1
        done
        run_cmd_retry zypper --non-interactive --gpg-auto-import-keys refresh

        # Now try again to install the newer version, where the bug is fixed.
        # Failing that, try to install the older version, before the bug existed.
        zypper --non-interactive in --force-resolution --no-confirm --no-recommends 'curl>=8.8'  || \
            zypper --non-interactive in --force-resolution --no-confirm --oldpackage --no-recommends 'curl<8.6'

        # Remove the backlevel repos so we don't pull other images from them
        S=5
        while [[ $S -lt $SP ]]; do
            remove_zypper_repos Module-Basesystem "$S"
            let S+=1
        done
    fi

    # And then lock the curl version so we don't change the version later
    run_cmd_retry zypper --non-interactive al curl
}

# Only need to apply the curl bug workaround if curl is installed
if rpm -q curl ; then
    apply_curl_bug_workaround
fi
#############################################################################

# Apply security patches (this script also does a zypper clean)
./zypper-refresh-patch-clean.sh
# Remove all repos & scrub the zypper directory 
run_cmd_retry zypper --non-interactive rr --all
rm -f /etc/zypp/repos.d/*
