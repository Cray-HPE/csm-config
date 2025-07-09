#!/bin/bash
#
# MIT License
#
# (C) Copyright 2024-2025 Hewlett Packard Enterprise Development LP
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

function get-token ()
{
    TOKEN=$(curl -s -S -d grant_type=client_credentials -d client_id=admin-client -d client_secret=`kubectl get secrets -n default admin-client-auth -o jsonpath='{.data.client-secret}' | base64 -d` "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token" | jq -r '.access_token')
}

function authcurl()
{
    get-token
    curl -H "Authorization: Bearer ${TOKEN}" "$@"
}

function hostname2xname()
{
    local HNAME="$1"
    authcurl -sk -X GET https://api-gw-service-nmn.local/apis/bss/boot/v1/bootparameters | jq -r '.[] | select(."cloud-init"."meta-data"."local-hostname" == "'${HNAME}'") | .hosts[0]' | head -n 1
}

# Use the presence of the iscsi Kubernetes label as the basis of which hosts to include
for h in $(kubectl get nodes -l iscsi=sbps -o custom-columns=:.metadata.name --no-headers); do
    xname=$(hostname2xname "${h}")
    NMN_IP="$( host $xname | grep "has address" | tail -n 1 | awk '{ print $NF }' )"
    HSN_IP="$( host ${xname}h0 | grep "has address" | tail -n 1 | awk '{ print $NF }' || true )"

    echo $h:$HSN_IP:$NMN_IP
done | sort -u
