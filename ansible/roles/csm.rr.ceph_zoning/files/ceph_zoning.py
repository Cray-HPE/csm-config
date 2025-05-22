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

"""
This script is used to apply CEPH zoning.
The objective of CEPH zoning is to make sure data gets replicated at rack level,
so there would not be data loss in case of a rack failure.
"""
import json
import subprocess
import re
import sys
import logging
import base64
from typing import Dict, List

# Set up logger
logger = logging.getLogger("CephZoning")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def run_command(command: str) -> str:
    """
    Helper function to run a shell command.
    command: is one of the command from yq, kubectl and ceph
    Returns result of the command output(stdout).
    """
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Command {command} errored out with : {e.stderr}") from e
    return result.stdout

def get_ceph_zone_prefix() -> str:
    """
    Get ceph zone prefix if defined from the site-init secret (customization).
    Return ceph_zone_prefix to be used by create_and_map_racks(positions_dict) function
    for mapping racks to zones.
    """
    namespace = "loftsman"
    secret_name = "site-init"
    secret = run_command(f"kubectl -n {namespace} get secret {secret_name} -o json")
    secret_data = json.loads(secret)
    encoded_yaml = secret_data["data"]["customizations.yaml"]
    decoded_yaml = base64.b64decode(encoded_yaml).decode("utf-8")
    output_file = "/tmp/customizations.yaml"
    with open(output_file, "w") as f:
        f.write(decoded_yaml)
    ceph_key_path = "spec.kubernetes.services.ceph_zone_prefix"
    # Run yq command to extract the value
    ceph_zone = run_command(f"yq r {output_file} {ceph_key_path}")
    ceph_zone_prefix = ceph_zone.strip()
    return ceph_zone_prefix

def create_and_map_racks(positions_dict: Dict[str, List[str]]) -> int:
    """
    Create ceph zones and map to management racks.
    positions_dict: dict of rack and corresponding management nodes(xnames)
    fetched from the rack placement file(/tmp/rack_info.txt).
    Here ceph zone name is: ceph zone prefix  + xname of the rack
    Return sn_count_in_rack (storage nodes per rack)
    """

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
            if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node):
                sn_count += 1
                logger.info(f"Moving storage node {node} to rack {rack}")
                run_command(f"ceph osd crush move {node} rack={rack}")

        sn_count_in_rack.append(sn_count)

    logger.debug(f"Storage node count per rack: {sn_count_in_rack}")
    return sn_count_in_rack

def create_and_apply_rules() -> None:
    """
    Create and apply a CRUSH rule with rack as the failure domain.
    Return nothing.
    """
    logger.info("Creating CRUSH rule with rack as failure domain")
    run_command("ceph osd crush rule create-replicated replicated_rule_with_rack_failure_domain default rack")

    ceph_pools = run_command("ceph osd pool ls").splitlines()

    for pool in ceph_pools:
        logger.debug(f"Applying new rule to pool: {pool}")
        run_command(f"ceph osd pool set {pool} crush_rule replicated_rule_with_rack_failure_domain")

def service_zoning(positions_dict: Dict[str, List[str]], sn_count_in_rack: int) -> None:
    """
    Perform service((MON, MGR, MDS) zoning.
    positions_dict: dict of rack and corresponding management nodes(xnames)
    fetched from the rack placement file(/tmp/rack_info.txt).
    sn_count_in_rack: number of storage nodes in a rack.
    Apply service zoning only if minimum 3 racks with storage nodes (at least one per rack) are present.
    Return nothing.
    """
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
        for nodes in positions_dict.values():
            for node in nodes:
                if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node) and node not in service_node_list:
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
    if nodes_count < 1:
        logger.error("ceph service node list is empty or storage nodes not found")
        sys.exit(1)
        
    # Apply services (MON, MGR, MDS)
    for service in ['mon', 'mgr', 'mds admin-tools', 'mds cephfs']:
        logger.info(f"Applying {service} service on nodes {nodes_output}")
        run_command(f"ceph orch apply {service} --placement=\"" + str(nodes_count) + " " + nodes_output + "\"")

    run_command("sleep 30")
    shell_script="/tmp/ceph_haproxy.sh"
    process = subprocess.Popen([shell_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

    # To capture and display output from the ceph_haproxy.sh script
    for line in process.stdout:
        logger.debug(line.strip())
    exit_code = process.wait()
    logger.debug(f"ceph_haproxy.sh exited with code {exit_code}")

def main() -> None:
    """ 
    Create ceph zones and map to racks, create and apply ceph CRUSH rule for each rack
    as the failure domain and perform ceph service zoning.
    rack_placement_file is a file with key value pair with xnames of
    racks and corresponding management nodes.
    """
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
