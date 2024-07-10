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

PDNS_API_KEY=$(kubectl -n services get secret cray-powerdns-credentials -o jsonpath='{.data.pdns_api_key}' | base64 -d)
PDNS_API=$(kubectl -n services get svc cray-dns-powerdns-api -o jsonpath='{.spec.clusterIP}')

hsn_srv_records=""
nmn_srv_records=""
hsn_a_records=""
nmn_a_records=""

system_name="$(cat /etc/environment | grep SYSTEM_NAME | awk -F= '{print $2;}')"

# - read each line from the file "/tmp/hsn_nmn_info.txt" passed on to this script
#   to fetch Host Name, HSN and NMN IP's for each worker node.
#   line format is: <Host Name>:<HSN IP>:<NMN IP>
# - then create DNS "SRV" and "A" records based on the above data
while read -r line; do
  ncn_worker_node=`echo "$line" | awk -F ":" '{print $1}'`
  iscsi_server_id="id-$(echo $ncn_worker_node | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"

  hsn_ip=`echo "$line" | awk -F ":" '{print $2}'` || true
  nmn_ip=`echo "$line" | awk -F ":" '{print $3}'`

  if [[ ! -z $hsn_ip ]]
  then
    hsn_srv_records="$hsn_srv_records{\"comments\": [], \"name\": \"_sbps-hsn._tcp."${system_name}".hpc.amslabs.hpecorp.net.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.hsn.${system_name}".hpc.amslabs.hpecorp.net.\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"SRV\"},"

    hsn_a_records="$hsn_a_records{\"comments\": [], \"name\": \"iscsi-server-"${iscsi_server_id}.hsn.${system_name}".hpc.amslabs.hpecorp.net.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${hsn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
  fi

  nmn_srv_records="$nmn_srv_records{\"comments\": [], \"name\": \"_sbps-nmn._tcp."${system_name}".hpc.amslabs.hpecorp.net.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.nmn.${system_name}".hpc.amslabs.hpecorp.net.\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"SRV\"},"

  nmn_a_records="$nmn_a_records{\"comments\": [], \"name\": \"iscsi-server-"${iscsi_server_id}.nmn.${system_name}".hpc.amslabs.hpecorp.net.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${nmn_ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
done

hsn_srv_records=`echo "${hsn_srv_records%?}"`
nmn_srv_records=`echo "${nmn_srv_records%?}"`
hsn_a_records=`echo "${hsn_a_records%?}"`
nmn_a_records=`echo "${nmn_a_records%?}"`

# PATCH (update) DNS "SRV" records for HSN and NMN for all the worker nodes
curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${system_name}.hpc.amslabs.hpecorp.net" -d'
{
  "rrsets": [
    '"${hsn_srv_records}"'

    '"${nmn_srv_records}"'
  ]
}'

if [[ ! -z $hsn_a_records ]]
then
  # PATCH (update) DNS  "A" records for HSN for all the worker nodes
  curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/hsn.${system_name}.hpc.amslabs.hpecorp.net" -d'
  {
    "rrsets": [
      '"${hsn_a_records}"'
    ]
  }'
fi

# PATCH (update) DNS  "A" records for NMN for all the worker nodes
curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/nmn.${system_name}.hpc.amslabs.hpecorp.net" -d'
{
  "rrsets": [
    '"${nmn_a_records}"'
  ]
}'
