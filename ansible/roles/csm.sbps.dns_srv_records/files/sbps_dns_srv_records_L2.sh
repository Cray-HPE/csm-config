#!/bin/bash
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
#
# Gate for the SBPS DNS SRV/A record configuration script.
#
#   both SRV records present  -> nothing runs
#   both SRV records missing  -> the configuration script is run as-is
#   only one missing          -> only that network (SRV + A records) is created
#
# The configuration script itself is not modified.
#
# Usage: sbps_dns_gate.sh [<config-script>] [<hsn_nmn_info-file>]
#

set -euo pipefail

DNS_SCRIPT="${1:-${SBPS_DNS_SCRIPT:-./sbps_dns_records.sh}}"
DNS_INPUT="${2:-${SBPS_DNS_INPUT:-/tmp/hsn_nmn_info.txt}}"

eval "$(grep -e SITE_DOMAIN -e SYSTEM_NAME /etc/environment)"

if [[ -z ${SITE_DOMAIN:-} || -z ${SYSTEM_NAME:-} ]]; then
  echo "ERROR: SITE_DOMAIN or SYSTEM_NAME is not set" 1>&2
  exit 1
fi

if [[ ! -r ${DNS_INPUT} ]]; then
  echo "ERROR: input file '${DNS_INPUT}' not found or not readable" 1>&2
  exit 1
fi

ZONE="${SYSTEM_NAME}.${SITE_DOMAIN}"

# --- check each network independently -------------------------------------
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
  echo "Neither HSN nor NMN SRV records exist - running ${DNS_SCRIPT}"
  exec "${DNS_SCRIPT}" < "${DNS_INPUT}"
fi

# --- exactly one network is missing: create only that one ------------------
if [[ ${hsn_present} -eq 0 ]]; then
  network="hsn"
  ip_field=2
else
  network="nmn"
  ip_field=3
fi

echo "Only ${network} is missing - creating ${network} records only"

echo "Getting PDNS_API_KEY"
PDNS_API_KEY=$(kubectl -n services get secret cray-powerdns-credentials -o jsonpath='{.data.pdns_api_key}' | base64 -d)

echo "Getting PDNS_API"
PDNS_API=$(kubectl -n services get svc cray-dns-powerdns-api -o jsonpath='{.spec.clusterIP}')

srv_records=""
a_records=""

while read -r line; do
  line=$(echo "$line" | tr -d '\r')
  if [[ -z ${line} ]]; then
    continue
  fi

  ncn_worker_node=$(echo "$line" | awk -F ":" '{print $1}')
  iscsi_server_id="id-$(echo "$ncn_worker_node" | awk -F "-" '{print $2}' | awk '{print substr($1,2);}')"
  ip=$(echo "$line" | awk -F ":" -v f="${ip_field}" '{print $f}')

  if [[ -z ${ip} ]]; then
    echo "Skipping ${ncn_worker_node}: no ${network} IP"
    continue
  fi

  srv_records="${srv_records}{\"content\": \"1 0 3260 iscsi-server-${iscsi_server_id}.${network}.${ZONE}.\",\"disabled\": false},"
  a_records="${a_records}{\"comments\": [], \"name\": \"iscsi-server-${iscsi_server_id}.${network}.${ZONE}.\",\"changetype\":\"REPLACE\",\"records\":[{\"content\": \"${ip}\",\"disabled\": false}],\"ttl\": 3600,\"type\": \"A\"},"
done < "${DNS_INPUT}"

if [[ -z ${srv_records} ]]; then
  echo "No ${network} records derived from ${DNS_INPUT} - nothing to do"
  exit 0
fi

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

echo DONE
