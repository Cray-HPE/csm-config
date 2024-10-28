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

get-token ()
{
    export TOKEN=$(curl -s -S -d grant_type=client_credentials -d client_id=admin-client -d client_secret=`kubectl get secrets admin-client-auth -o jsonpath='{.data.client-secret}' | base64 -d` "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token" | jq -r '.access_token')
}

function authcurl()
{
    get-token
    curl -H "Authorization: Bearer ${TOKEN}" "$@"
}

function xname2hostname()
{
    local XNAME="$1"
    authcurl -sk -X GET https://api-gw-service-nmn.local/apis/sls/v1/hardware/${XNAME} | jq .ExtraProperties.Aliases[] -r | head -n 1
}

for h in $( authcurl -s "https://api-gw-service-nmn.local/apis/smd/hsm/v2/State/Components?role=Management&subrole=Worker" | jq .Components[].ID -r ); do
    NMN_IP="$( host $h | grep "has address" | tail -n 1 | awk '{ print $NF }' )"
    HSN_IP="$( host ${h}h0 | grep "has address" | tail -n 1 | awk '{ print $NF }' || true )"
    RHOST="$( xname2hostname $h )"

    echo $RHOST:$HSN_IP:$NMN_IP
done | sort
