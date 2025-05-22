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
# Also, this updates ceph.conf accross all storage nodes with latest configuration. 

echo "Generating minimal configuration and copying updated ceph.conf"
ceph config generate-minimal-conf > /etc/ceph/ceph_conf_min
cp /etc/ceph/ceph_conf_min /etc/ceph/ceph.conf
for host in $(ceph node ls| jq -r '.osd|keys[]'); do
  echo "Copying ceph.conf to $host"
  scp /etc/ceph/ceph.conf $host:/etc/ceph
done

for host in $(ceph node ls| jq -r '.osd|keys[]'); do
  ssh -T -q $host << 'EOF'
    haproxy_temp_file="/etc/haproxy/haproxy_temp.cfg"
    /srv/cray/scripts/metal/generate_haproxy_cfg.sh > $haproxy_temp_file

    hosts=$(sed -n 's/.*server server-\([a-z0-9\-]*\)-mgr :3000 check weight 100.*/\1/p' "$haproxy_temp_file")
    echo "grafana-backend entries in haproxy config that are missing IPs are - \"${hosts}\""
    for host in $hosts; do
      ip=$(ceph mon dump | grep ${host} | awk '{ print $2 }' |  awk -F'[:,/]' '{print $2}')
      old_pattern="server server-$host-mgr :3000 check weight 100"
      new_pattern="server server-$host-mgr $ip:3000 check weight 100"
      echo "Updated entry with IP for grafana-backend section - \"${new_pattern}\""
      sed -i "s|$old_pattern|$new_pattern|" "$haproxy_temp_file"
    done

    hosts=$(sed -n 's/.*server server-\([a-z0-9\-]*\)-rgw0 :8080 check weight 100.*/\1/p' "$haproxy_temp_file")
    echo "rgw-backend entries in haproxy config that are missing IPs are - \"${hosts}\""
    for host in $hosts; do
      ip=$(ceph mon dump | grep ${host} | awk '{ print $2 }' |  awk -F'[:,/]' '{print $2}')
      old_pattern="server server-$host-rgw0 :8080 check weight 100"
      new_pattern="server server-$host-rgw0 $ip:8080 check weight 100"
      echo "Updated entry with IP for rgw-backend section - \"${new_pattern}\""
      sed -i "s|$old_pattern|$new_pattern|" "$haproxy_temp_file"
    done

    hosts=$(sed -n 's/.*server server-\([a-z0-9\-]*\)-mgr :8443 check weight 100.*/\1/p' "$haproxy_temp_file")
    echo "dashboard_back_ssl entries in haproxy config that are missing IPs are - \"${hosts}\""
    for host in $hosts; do
      ip=$(ceph mon dump | grep ${host} | awk '{ print $2 }' |  awk -F'[:,/]' '{print $2}')
      old_pattern="server server-$host-mgr :8443 check weight 100"
      new_pattern="server server-$host-mgr $ip:8443 check weight 100"
      echo "Updated entry with IP for dashboard_back_ssl section - \"${new_pattern}\""
      sed -i "s|$old_pattern|$new_pattern|" "$haproxy_temp_file"
    done

mv $haproxy_temp_file /etc/haproxy/haproxy.cfg
systemctl enable haproxy.service
systemctl restart haproxy.service
EOF
done
