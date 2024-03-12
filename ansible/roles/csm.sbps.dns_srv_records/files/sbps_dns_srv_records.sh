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

set -eu pipefail
#set -euo pipefail

PDNS_API_KEY=$(kubectl -n services get secret cray-powerdns-credentials -o jsonpath='{.data.pdns_api_key}' | base64 -d)
PDNS_API=$(kubectl -n services get svc cray-dns-powerdns-api -o jsonpath='{.spec.clusterIP}')

system_name="$(cat /etc/cray/system_name)"
#system_name="odin"
echo "System Name: $system_name"

##host_name="$(awk '{print $1}' /etc/hostname)"
##echo "Host Name: $host_name"

##iscsi_server_id="$(echo $host_name | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"
##echo "iscsi server id: $iscsi_server_id"

hsn_ip="$(ip addr | grep "hsn0$" | awk '{print $2;}' | awk -F\/ '{print $1;}')"
nmn_ip="$(ip addr | grep "nmn0$" | awk '{print $2;}' | awk -F\/ '{print $1;}')"
echo "HSN IP: $hsn_ip"
echo "NMN IP: $nmn_ip"

hsn_records=""
nmn_records=""

##
ncn_nodes=("ncn-w005" "ncn-w006")
for ncn_node in "${ncn_nodes[@]}"
do
  echo $ncn_node
  iscsi_server_id="$(echo $ncn_node | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"
  hsn_srv_records="$hsn_srv_records{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.hsn.${system_name}".hpc.amslabs.hpecorp.net.\",\"disabled\": false},"
  nmn_srv_records="$nmn_srv_records{\"content\": \"1 0 3260 iscsi-server-"${iscsi_server_id}.nmn.${system_name}".hpc.amslabs.hpecorp.net.\",\"disabled\": false},"
  hsn_a_records="$hsn_a_records{\"content\": \"'"${hsn_ip}"'\",},\"disabled\": false},"
  nmn_a_records="$nmn_a_records{\"content\": \"'"${nmn_ip}"'\",},\"disabled\": false},"
done

hsn_srv_records=`echo "${hsn_srv_records%?}"`
nmn_srv_records=`echo "${nmn_srv_records%?}"`
hsn_a_records=`echo "${hsn_a_records%?}"`
nmn_a_records=`echo "${nmn_a_records%?}"`
 
echo "hsn_srv_records: $hsn_srv_records"
echo "nmn_srv_records: $nmn_srv_records"
echo "hsn_a_records: $hsn_a_records"
echo "nmn_a_records:$nmn_a_records"
##

#exit 1

curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/${system_name}.hpc.amslabs.hpecorp.net" -d'
{
  "rrsets": [
    {
      "comments": [],
      "name": "_sbps-hsn._tcp.'"${system_name}"'.hpc.amslabs.hpecorp.net.",
      "changetype": "REPLACE",
      "records": [
	'"${hsn_srv_records}"'
      ],
      "ttl": 3600,
      "type": "SRV"
    },
    {
      "comments": [],
      "name": "_sbps-nmn._tcp.'"${system_name}"'.hpc.amslabs.hpecorp.net.",
      "changetype": "REPLACE",
      "records": [
	'"${nmn_srv_records}"'
      ],
      "ttl": 3600,
      "type": "SRV"
    }
  ]
}'

curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/hsn.${system_name}.hpc.amslabs.hpecorp.net" -d'
{
  "rrsets": [
    {
      "comments": [],
      "name": "iscsi-server-'"${iscsi_server_id}.hsn.${system_name}"'.hpc.amslabs.hpecorp.net.",
      "changetype": "REPLACE",
      "records": [
        '"${hsn_a_records}"'
      ],
      "ttl": 3600,
      "type": "A"
    }
  ]
}'

curl -s -X PATCH -H "X-API-Key: ${PDNS_API_KEY}" "http://${PDNS_API}:8081/api/v1/servers/localhost/zones/nmn.${system_name}.hpc.amslabs.hpecorp.net" -d'
{
  "rrsets": [
    {
      "comments": [],
      "name": "iscsi-server-'"${iscsi_server_id}.nmn.${system_name}"'.hpc.amslabs.hpecorp.net.",
      "changetype": "REPLACE",
      "records": [
        '"${nmn_a_records}"'
      ],
      "ttl": 3600,
      "type": "A"
    }
  ]
}'
