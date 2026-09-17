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
    # - read each line from the file /tmp/hsn_nmn_info.txt passed on to this script
    #   to fetch Host Name, HSN and NMN IP's for each worker node.
    #   line format is: <Host Name>:<HSN IP>:<NMN IP>
    # - then create DNS SRV and A records based on the above data
    while read -r line; do
        # Strip out any '\r' characters
        line=$(echo "$line" | tr -d '\r')

        echo "Getting worker node name"
        ncn_worker_node=$(echo "$line" | awk -F ":" '{print $1}')

        echo "Getting iSCSI server ID"
        iscsi_server_id="id-$(echo "$ncn_worker_node" | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"

        echo "Getting hsn_ip"
        hsn_ip=$(echo "$line" | awk -F ":" '{print $2}') || true

        echo "Getting nmn_ip"
        nmn_ip=$(echo "$line" | awk -F ":" '{print $3}')

        if [[ -n $hsn_ip ]]
        then
            echo "Appending to hsn_srv_records"
            hsn_srv_records="$hsn_srv_records{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.hsn.${SYSTEM_NAME}.${SITE_DOMAIN}."\",\"disabled\": false},"
            echo "Appending to hsn_a_records"
            hsn_a_records="$hsn_a_records{\"comments\": [], \"name\": \"iscsi-server-"${iscsi_server_id}.hsn.${SYSTEM_NAME}.${SITE_DOMAIN}."\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${hsn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
        fi

        echo "Appending to nmn_srv_records"
        nmn_srv_records="$nmn_srv_records{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.nmn.${SYSTEM_NAME}.${SITE_DOMAIN}."\",\"disabled\": false},"
        echo "Appending to nmn_a_records"
        nmn_a_records="$nmn_a_records{\"comments\": [], \"name\": \"iscsi-server-"${iscsi_server_id}.nmn.${SYSTEM_NAME}.${SITE_DOMAIN}."\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${nmn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
    done

    hsn_srv_records="${hsn_srv_records%?}"
    echo "hsn_srv_records: ${hsn_srv_records}"

    nmn_srv_records="${nmn_srv_records%?}"
    echo "nmn_srv_records: ${nmn_srv_records}"

    hsn_a_records="${hsn_a_records%?}"
    echo "hsn_a_records: ${hsn_a_records}"

    nmn_a_records="${nmn_a_records%?}"
    echo "nmn_a_records: ${nmn_a_records}"

    echo "Patch SRV records"
    # PATCH (update) DNS "SRV" records for HSN and NMN for all the worker nodes
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${SYSTEM_NAME}.${SITE_DOMAIN}" -d'
    {
      "rrsets": [
        {
          "comments": [],
          "name": "_sbps-hsn._tcp.'"${SYSTEM_NAME}"'.'"${SITE_DOMAIN}."'",
          "changetype":"REPLACE",
          "records":[
            '"${hsn_srv_records}"'
          ],
          "ttl": 3600,
          "type": "SRV"
        },
        {
          "comments": [],
          "name": "_sbps-nmn._tcp.'"${SYSTEM_NAME}"'.'"${SITE_DOMAIN}."'",
          "changetype":"REPLACE",
          "records":[
            '"${nmn_srv_records}"'
          ],
          "ttl": 3600,
          "type": "SRV"
        }
      ]
    }'

    # PATCH (update) DNS  "A" records for HSN for all the worker nodes
    echo "Patch HSN A records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/hsn.${SYSTEM_NAME}.${SITE_DOMAIN}" -d'
    {
      "rrsets": [
        '"${hsn_a_records}"'
      ]
    }'

    # PATCH (update) DNS  "A" records for NMN for all the worker nodes
    echo "Patch NMN A records"
    curl -i -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/nmn.${SYSTEM_NAME}.${SITE_DOMAIN}" -d'
    {
      "rrsets": [
        '"${nmn_a_records}"'
      ]
    }'
}

# - Configure HSN or NMN SRV records
function configure_hsn_or_nmn ()
{
    # - read each line from the file /tmp/hsn_nmn_info.txt passed on to this script
    #   to fetch Host Name, HSN and NMN IP's for each worker node.
    #   line format is: <Host Name>:<HSN IP>:<NMN IP>
    # - then create DNS SRV and A records for the missing network

    local network="$1"
    local ip_field="$2"

    echo "Nwtwork: $network IP Field: $ip_field"

    srv_records=""
    a_records=""

    while read -r line; do
        # Strip out any '\r' characters
        line=$(echo "$line" | tr -d '\r')

        echo "Getting worker node name"
        ncn_worker_node=$(echo "$line" | awk -F ":" '{print $1}')

        echo "Getting iSCSI server ID"
        iscsi_server_id="id-$(echo "$ncn_worker_node" | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"

        echo "Getting hsn_ip or nmn_ip"
        ip=$(echo "$line" | awk -F ":" -v f="${ip_field}" '{print $f}')

        if [[ -z ${ip} ]]; then
            echo "Skipping ${ncn_worker_node}: no ${network} IP"
            continue
        fi

        echo "Appending to hsn or nmn srv_records"
        srv_records="${srv_records}{\"content\": \"1 0 3260 iscsi-server-${iscsi_server_id}.${network}.${ZONE}.\",\"disabled\": false},"

        echo "Appending to hsn or nmn a_records"
        a_records="${a_records}{\"comments\": [], \"name\": \"iscsi-server-${iscsi_server_id}.${network}.${ZONE}.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
    done

    srv_records="${srv_records%?}"
    a_records="${a_records%?}"

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

hsn_srv_records=""
nmn_srv_records=""
hsn_a_records=""
nmn_a_records=""

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

# - check each network independently
hsn_present=0
nmn_present=0

if [[ -n $(dig +short -t SRV "_sbps-hsn._tcp.${ZONE}") ]]; then
  hsn_present=1
fi

if [[ -n $(dig +short -t SRV "_sbps-nmn._tcp.${ZONE}") ]]; then
  nmn_present=1
fi

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
  ip_field=2
else
  echo "Only HSN SRV records exist - configure the missing NMN SRV records."
  network="nmn"
  ip_field=3
fi
configure_hsn_or_nmn $network $ip_field

echo DONE
