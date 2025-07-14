#!/usr/bin/env bash
#
# MIT License
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
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

# When CEPH services distribution is modified as a result of CEPH zoning,
# there would be entries in haproxy with missing IPs which is updated using this script.
# Also, this script updates ceph.conf accross all storage nodes with latest configuration.

set -euo pipefail

log() {
    echo "[INFO] $1"
}

fail() {
    echo "[ERROR] $1" >&2
    exit 1
}

log "Updating ceph.conf with latest configuration"
ceph config generate-minimal-conf > /etc/ceph/ceph_conf_min || fail "Failed to generate ceph configuration"
cp /etc/ceph/ceph_conf_min /etc/ceph/ceph.conf || fail "Failed to copy ceph configuration to /etc/ceph/ceph.conf"

log "Generating temporary haproxy config"
haproxy_temp_file="/etc/haproxy/haproxy_temp.cfg"
srv/cray/scripts/metal/generate_haproxy_cfg.sh > "$haproxy_temp_file" || fail "Failed to generate haproxy config"

log "Parsing generated haproxy config"
hosts_found=false

sections=("mgr:3000:grafana-backend" "rgw0:8080:rgw-backend" "mgr:8443:dashboard_back_ssl")
for section in "${sections[@]}"; do
    svc=$(echo "$section" | cut -d':' -f1)
    port=$(echo "$section" | cut -d':' -f2)
    label=$(echo "$section" | cut -d':' -f3)

    log "Processing section: $label (svc=$svc, port=$port)"

    hosts=$(sed -n "s/.*server server-\([a-z0-9\-]*\)-$svc :$port check weight 100.*/\1/p" "$haproxy_temp_file") || fail "Failed to parse hosts for $label"

    if [ -z "$hosts" ]; then
        log "No entries with missing IPs found for $label"
        continue
    else
        log "$label contains entries with missing IPs for hosts - $hosts"
        hosts_found=true
    fi

    for host in $hosts; do
        ip=$(ceph mon dump | grep "${host}" | awk '{ print $2 }' | awk -F'[:,/]' '{print $2}') || fail "Failed to get IP for host $host"

        if [ -z "$ip" ]; then
            fail "Could not resolve IP for host $host"
        fi

        old_pattern="server server-$host-$svc :$port check weight 100"
        new_pattern="server server-$host-$svc ${ip}:$port check weight 100"

        log "Updating $label config for host $host: $old_pattern -> $new_pattern"

        sed -i "s|$old_pattern|$new_pattern|" "$haproxy_temp_file" || fail "Failed to update haproxy config for $host"
    done
done

if [ "$hosts_found" = true ]; then
    log "Replacing haproxy.cfg with updated config"
    mv "$haproxy_temp_file" /etc/haproxy/haproxy.cfg || fail "Failed to replace haproxy.cfg"

    log "Enabling haproxy.service"
    systemctl enable haproxy.service || fail "Failed to enable haproxy.service"

    log "Restarting haproxy.service"
    systemctl restart haproxy.service || fail "Failed to restart haproxy.service"

    log "HAProxy config update completed successfully!"
fi
