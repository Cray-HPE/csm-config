#!/bin/bash
#
# MIT License
#
# (C) Copyright 2024-2026 Hewlett Packard Enterprise Development LP
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

# - Configure both HSN and NMN SRV records
function configure_hsn_and_nmn ()
{
    echo "Patch SRV records"
    # PATCH (update) DNS "SRV" records for HSN and NMN
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${ZONE}" -d'
    {
      "rrsets": [
        {
          "comments": [],
          "name": "_sbps-hsn._tcp.'"${ZONE}."'",
          "changetype":"REPLACE",
          "records":[
            '"${hsn_srv_records}"'
          ],
          "ttl": 3600,
          "type": "SRV"
        },
        {
          "comments": [],
          "name": "_sbps-nmn._tcp.'"${ZONE}."'",
          "changetype":"REPLACE",
          "records":[
            '"${nmn_srv_records}"'
          ],
          "ttl": 3600,
          "type": "SRV"
        }
      ]
    }'

    # PATCH (update) DNS  "A" records for HSN
    echo "Patch HSN A records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/hsn.${ZONE}" -d'
    {
      "rrsets": [
        '"${hsn_a_records}"'
      ]
    }'

    # PATCH (update) DNS  "A" records for NMN
    echo "Patch NMN A records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/nmn.${ZONE}" -d'
    {
      "rrsets": [
        '"${nmn_a_records}"'
      ]
    }'
}

# - Configure HSN or NMN SRV records
function configure_hsn_or_nmn ()
{
    local network="$1"
    local srv_records a_records

    echo "Nwtwork: $network"

    srv_records=""
    a_records=""

    if [[ ${network} == "hsn" ]]; then
        srv_records="${hsn_srv_records}"
        a_records="${hsn_a_records}"
    else
        srv_records="${nmn_srv_records}"
        a_records="${nmn_a_records}"
    fi

    echo "Patch ${network} SRV records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${ZONE}" -d'
    {
      "rrsets": [
        {
          "comments": [],
          "name": "_sbps-'"${network}"'._tcp.'"${ZONE}."'",
          "changetype":"REPLACE",
          "records":[
            '"${srv_records}"'
          ],
          "ttl": 3600,
          "type": "SRV"
        }
      ]
    }'

    echo "Patch ${network} A records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${network}.${ZONE}" -d'
    {
      "rrsets": [
        '"${a_records}"'
      ]
    }'
}

echo "Getting PDNS_API_KEY"
PDNS_API_KEY=$(kubectl -n services get secret cray-powerdns-credentials -o jsonpath='{.data.pdns_api_key}' | base64 -d)

echo "Getting PDNS_API"
PDNS_API=$(kubectl -n services get svc cray-dns-powerdns-api -o jsonpath='{.spec.clusterIP}')

echo "Setting SITE_DOMAIN and SYSTEM_NAME from /etc/environment"
eval "$(grep -e SITE_DOMAIN -e SYSTEM_NAME /etc/environment)"

echo "SITE_DOMAIN: '${SITE_DOMAIN}'"
echo "SYSTEM_NAME: '${SYSTEM_NAME}'"

if [[ -z ${SITE_DOMAIN} ]]; then
  echo "ERROR: SITE_DOMAIN is not set" 1>&2
  exit 1
fi

if [[ -z ${SYSTEM_NAME} ]]; then
  echo "ERROR: SYSTEM_NAME is not set" 1>&2
  exit 1
fi

ZONE="${SYSTEM_NAME}.${SITE_DOMAIN}"

hsn_srv_records=""
nmn_srv_records=""
hsn_a_records=""
nmn_a_records=""

declare -A expected_hsn_ip=()
declare -A expected_nmn_ip=()

# - read each line from the file /tmp/hsn_nmn_info.txt passed on to this script
#   to fetch Host Name, HSN and NMN IP's for each worker node.
#   line format is: <Host Name>:<HSN IP>:<NMN IP>
# - then create expected DNS SRV and A records based on the above data after validation.
while IFS= read -r line || [[ -n ${line} ]]; do
    # strip '\r' and split the row in one pass - no tr/awk subprocesses
    IFS=':' read -r ncn_worker_node hsn_ip nmn_ip _ <<< "${line//$'\r'/}"

    # ignore anything that is not a worker record (e.g. kubectl warnings)
    [[ ${ncn_worker_node} =~ ^ncn-w[0-9]{3}$ ]] || continue

    # ncn-w004 -> id-004
    iscsi_server_id="${ncn_worker_node#*-}"
    iscsi_server_id="id-${iscsi_server_id:1}"

    if [[ -n ${hsn_ip} ]]; then
        target="iscsi-server-${iscsi_server_id}.hsn.${ZONE}."
        expected_hsn_ip["${target}"]="${hsn_ip}"
        hsn_srv_records="${hsn_srv_records}{\"content\": \"1 0 3260 ${target}\",\"disabled\": false},"
        hsn_a_records="${hsn_a_records}{\"comments\": [], \"name\": \"${target}\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${hsn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
    fi

    if [[ -n ${nmn_ip} ]]; then
        target="iscsi-server-${iscsi_server_id}.nmn.${ZONE}."
        expected_nmn_ip["${target}"]="${nmn_ip}"
        nmn_srv_records="${nmn_srv_records}{\"content\": \"1 0 3260 ${target}\",\"disabled\": false},"
        nmn_a_records="${nmn_a_records}{\"comments\": [], \"name\": \"${target}\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${nmn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
    fi
done

hsn_srv_records="${hsn_srv_records%,}"
nmn_srv_records="${nmn_srv_records%,}"
hsn_a_records="${hsn_a_records%,}"
nmn_a_records="${nmn_a_records%,}"

if [[ -z ${hsn_srv_records} && -z ${nmn_srv_records} ]]; then
  echo "ERROR: no valid <hostname>:<hsn-ip>:<nmn-ip> records on stdin;" 1>&2
  echo "       refusing to REPLACE the SBPS SRV record sets with an empty list" 1>&2
  exit 1
fi

# - Validation - per record, not just "does the RRset exist"
published_hsn_srv=$(dig +short -t SRV "_sbps-hsn._tcp.${ZONE}" | awk '{ print $NF }')
published_nmn_srv=$(dig +short -t SRV "_sbps-nmn._tcp.${ZONE}" | awk '{ print $NF }')

hsn_present=1
nmn_present=1

for target in "${!expected_hsn_ip[@]}"; do
    if ! grep -qxF "${target}" <<< "${published_hsn_srv}"; then
        echo "HSN SRV record missing: ${target}"
        hsn_present=0
    elif ! dig +short -t A "${target}" | grep -qxF "${expected_hsn_ip[${target}]}"; then
        echo "HSN A record missing or stale: ${target} (expected ${expected_hsn_ip[${target}]})"
        hsn_present=0
    fi
done

for target in "${!expected_nmn_ip[@]}"; do
    if ! grep -qxF "${target}" <<< "${published_nmn_srv}"; then
        echo "NMN SRV record missing: ${target}"
        nmn_present=0
    elif ! dig +short -t A "${target}" | grep -qxF "${expected_nmn_ip[${target}]}"; then
        echo "NMN A record missing or stale: ${target} (expected ${expected_nmn_ip[${target}]})"
        nmn_present=0
    fi
done

echo "_sbps-hsn._tcp.${ZONE} present: ${hsn_present}"
echo "_sbps-nmn._tcp.${ZONE} present: ${nmn_present}"

if [[ ${hsn_present} -eq 1 && ${nmn_present} -eq 1 ]]; then
  echo "Both HSN and NMN SRV records already exist - nothing to do"
  exit 0
fi

if [[ ${hsn_present} -eq 0 && ${nmn_present} -eq 0 ]]; then
  echo "Neither HSN nor NMN SRV records exist - configure both"
  configure_hsn_and_nmn
  echo DONE
  exit 0
fi

# - exactly one network is missing: create only that one
if [[ ${hsn_present} -eq 0 ]]; then
  echo "Only NMN SRV records exist - configure the missing HSN SRV records."
  network="hsn"
else
  echo "Only HSN SRV records exist - configure the missing NMN SRV records."
  network="nmn"
fi
configure_hsn_or_nmn "$network"

echo DONE
