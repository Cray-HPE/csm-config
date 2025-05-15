#!/usr/bin/python3
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

#This script is used to apply CEPH zoning
#The objective of CEPH zoning is to make sure data gets replicated at rack level, so there would not be data loss incase of a rack failure

import json
import subprocess
import re
import sys
import logging
import base64

# Set up logger
logger = logging.getLogger("CephZoning")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def get_ceph_zone_prefix():
    # Run kubectl command and capture JSON output
    namespace = "loftsman"
    secret_name = "site-init"

    kubectl_cmd = ["kubectl", "-n", namespace, "get", "secret", secret_name, "-o", "json"]
    kubectl_output = subprocess.run(kubectl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

    # Parse JSON output
    secret_data = json.loads(kubectl_output.stdout)

    # Extract and decode the base64 data
    encoded_yaml = secret_data["data"]["customizations.yaml"]
    decoded_yaml = base64.b64decode(encoded_yaml).decode("utf-8")

    # Write the yaml output to a file
    output_file = "/tmp/customizations.yaml"
    with open(output_file, "w") as f:
        f.write(decoded_yaml)

    # Define the key path
    output_file = "/tmp/customizations1.yaml"
    ceph_key_path = "spec.kubernetes.services.ceph_zone_prefix"

    # Run yq command to extract the value
    ceph_yq_cmd = ["yq", "r", output_file, ceph_key_path]
    ceph_zone = subprocess.run(ceph_yq_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

    # Extract and clean the output
    ceph_zone_prefix = ceph_zone.stdout.strip()
    return ceph_zone_prefix

def run_command(command):
    """Helper function to run a command and return the result."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Command {command} errored out with : {e.stderr}")
    return result.stdout

def create_and_map_racks(positions_dict):
    sn_count_in_rack = []

    for rack, nodes in positions_dict.items():
        # Updating the rack or zone prefix
        ceph_zone_prefix = get_ceph_zone_prefix()
        if ceph_zone_prefix:
            rack = ceph_zone_prefix + "-" + rack
        # Create buckets for racks
        logger.info(f"Creating bucket for rack: {rack}")
        run_command(f"ceph osd crush add-bucket {rack} rack")
        run_command(f"ceph osd crush move {rack} root=default")

        sn_count = 0
        for node in nodes:
            # Storage node match
            if re.match(r"^.*ncn-s[0-9][0-9][1-9]$", node):
                sn_count += 1
                logger.info(f"Moving storage node {node} to rack {rack}")
                run_command(f"ceph osd crush move {node} rack={rack}")

        sn_count_in_rack.append(sn_count)

    logger.debug(f"Storage node count per rack: {sn_count_in_rack}")
    return sn_count_in_rack

def create_and_apply_rules():
    # Create and apply a CRUSH rule with Rack as the failure domain
    logger.info("Creating CRUSH rule with rack as failure domain")
    run_command("ceph osd crush rule create-replicated replicated_rule_with_rack_failure_domain default rack")

    ceph_pools = run_command("ceph osd pool ls").splitlines()

    for pool in ceph_pools:
        logger.debug(f"Applying new rule to pool: {pool}")
        run_command(f"ceph osd pool set {pool} crush_rule replicated_rule_with_rack_failure_domain")

def service_zoning(positions_dict, sn_count_in_rack):
    service_node_list = []
    mon_count = 0
    command = "ceph node ls | jq '.osd | keys | length'"
    number_of_nodes = int(run_command(command))

    if len([x for x in sn_count_in_rack if x > 0]) < 3:
        logger.error("Minimum 3 racks with storage nodes are needed for optimal distribution of CEPH data")
        sys.exit(1)

    if number_of_nodes in [3, 4]:
        mon_count = 3
    elif number_of_nodes >= 5:
        mon_count = 5
        # Incase of 5 monitors, there should be atleast 3 monitors running for establishing quorum.
        # But if 3 mons are on same rack(like in 3,1,1 distribution), there is a chance that CEPH would not be functional when that rack goes down.
        # So configuring only 3 monitors instead of 5 each in one rack in this scenario.
        if number_of_nodes-2 in sn_count_in_rack:
            mon_count = 3

    logger.debug(f"Monitor desired count: {mon_count}")
    count = 0

   # Select the storage nodes on which the services are to be run in round robin way across racks
    while count < mon_count:
        for rack, nodes in positions_dict.items():
            for node in nodes:
                if re.match(r"^.*ncn-s[0-9][0-9][1-9]$", node) and node not in service_node_list:
                    service_node_list.append(node)
                    count += 1
                    break
            if count == mon_count:
                break
        if count == mon_count:
            break

    logger.debug(f"Selected nodes on which CEPH services be running: {service_node_list}")
    nodes_output = " ".join(service_node_list)
    nodes_count = len(service_node_list)

    # Apply services (MON, MGR, MDS)
    for service in ['mon', 'mgr', 'mds admin-tools', 'mds cephfs']:
        logger.info(f"Applying {service} service on nodes {nodes_output}")
        run_command(f"ceph orch apply {service} --placement=\"" + str(nodes_count) + " " + nodes_output + "\"")

    # Configurations
    logger.info("Generating minimal configuration and copying updated ceph.conf")
    run_command("sleep 30")
    run_command("ceph config generate-minimal-conf > /etc/ceph/ceph_conf_min")
    run_command("cp /etc/ceph/ceph_conf_min /etc/ceph/ceph.conf")
    run_command("for host in $(ceph node ls| jq -r '.osd|keys[]'); do scp /etc/ceph/ceph.conf $host:/etc/ceph; done")
    

def main():
    if len(sys.argv) != 2:
        logger.error("Usage: python ceph_zoning.py <rack_placement_file>")
        sys.exit(1)

    # Load the rack placement file
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as file:
            positions_dict = json.load(file)
    except Exception as e:
        logger.error(f"Failed to load the rack placement file: {e}")
        sys.exit(1)

    # Create and map racks, create rules, and perform service zoning
    sn_count_in_rack = create_and_map_racks(positions_dict)
    create_and_apply_rules()
    service_zoning(positions_dict, sn_count_in_rack)

if __name__ == "__main__":
    main()
