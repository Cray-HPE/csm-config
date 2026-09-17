#!/bin/bash
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
#
# Gate for the SBPS DNS SRV/A record configuration script.
# If the SBPS SRV records already exist, the configuration script is never
# invoked. The configuration script itself is not modified.
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

for rec in "_sbps-hsn._tcp.${SYSTEM_NAME}.${SITE_DOMAIN}" "_sbps-nmn._tcp.${SYSTEM_NAME}.${SITE_DOMAIN}"; do
  if [[ -n $(dig +short -t SRV "${rec}") ]]; then
    echo "${rec} already exists - not running ${DNS_SCRIPT}"
    exit 0
  fi
done

echo "No SBPS SRV records found - running ${DNS_SCRIPT}"
#exec "${DNS_SCRIPT}" < "${DNS_INPUT}"
