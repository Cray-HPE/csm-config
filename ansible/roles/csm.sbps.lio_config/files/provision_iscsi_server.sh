#!/bin/bash
#
# MIT License
#
# (C) Copyright 2024 Hewlett Packard Enterprise Development LP
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

set -euo pipefail

IQN_PREFIX="iqn.2023-06.csm.iscsi:"

# Before anything else, check to see if iSCSI/LIO is already
# configured.  In that case, do nothing as we don't want to
# wipe out the existing configuration.
if targetcli ls "/iscsi/${IQN_PREFIX}${HOST}" >& /dev/null; then
        echo "Skipping configuring LIO because it appears to already be configured"
        exit 0
fi

function clear_server_config()
{
        # Make a back-up copy of the current config, just in case
        targetcli saveconfig /etc/target/saveconfig.$(date +%Y%m%d%H%M%S).json &> /dev/null
        targetcli clearconfig confirm=True &> /dev/null
}

function save_server_config()
{
        targetcli saveconfig &> /dev/null
}

function add_server_target()
{
        TARGET_SERVER_IQN="${IQN_PREFIX}${HOST}"
        targetcli "/iscsi create $TARGET_SERVER_IQN" &> /dev/null
        targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1/portals delete ip_address=0.0.0.0 ip_port=3260" &> /dev/null
        targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1/portals create ${NMN_IP}" &> /dev/null

        if [[ -n $HSN_IP ]]
        then
          targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1/portals create ${HSN_IP}" &> /dev/null
        fi

        targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1 set attribute demo_mode_write_protect=1" &> /dev/null
        targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1 set attribute prod_mode_write_protect=1" &> /dev/null
        echo "$TARGET_SERVER_IQN"
}

function auto_generate_node_acls()
{
        TARGET_SERVER_IQN="$1"
        targetcli "/iscsi/${TARGET_SERVER_IQN}/tpg1 set attribute generate_node_acls=1"
}

#--------------------------------------------------------------------
# Base Target Configuration
#--------------------------------------------------------------------

HSN_IP="$(ip addr | grep "hsn0$")" || true

if [[ -n $HSN_IP ]]
then
  HSN_IP="$(echo "$HSN_IP" | awk '{print $2;}' | awk -F/ '{print $1;}')"
fi

NMN_IP="$(host -4 "${HOST}.nmn" | awk '{print $NF;}')"

systemctl stop target
systemctl enable --now target
clear_server_config
SERVER_IQN="$(add_server_target)"

#--------------------------------------------------------------------
# Configure automatic intiator mappings when they attempt to connect
#--------------------------------------------------------------------

auto_generate_node_acls "$SERVER_IQN"
save_server_config
