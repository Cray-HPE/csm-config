#!/usr/bin/python3
#
# MIT License
#
# (C) Copyright 2025-2026 Hewlett Packard Enterprise Development LP
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
import time
from typing import Dict, List

# Set up logger
logger = logging.getLogger("CephZoning")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def run_command(command: str, timeout: int = 300) -> str:
    """
    Helper function to run a shell command.
    Args:
        command (str): The shell command to run.
        timeout (int): Seconds to wait before the command is killed.
    Returns:
        str: The output of the command.
    """
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, check=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"Command timed out: {command}") from e
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Command {command} errored out with : {e.stderr}") from e
    return result.stdout


def get_current_crush_rack_mapping() -> Dict[str, str]:
    """
    Get the current storage node to rack mapping from the CRUSH tree.
    Returns:
        Dict[str, str]: A dictionary mapping storage node hostnames to their rack names.
    """
    result = run_command("ceph osd crush tree --format json")
    tree = json.loads(result)
    node_to_rack: Dict[str, str] = {}
    for node in tree.get("nodes", []):
        if node.get("type") == "rack":
            rack_name = node["name"]
            for child_id in node.get("children", []):
                for n in tree["nodes"]:
                    if n["id"] == child_id and n["type"] == "host":
                        node_to_rack[n["name"]] = rack_name
    return node_to_rack


def get_current_service_hosts(service_type: str) -> List[str]:
    """
    Get the sorted list of hostnames where a given Ceph service type is currently running.
    Args:
        service_type (str): The Ceph daemon type (e.g., 'mon', 'mgr', 'mds').
    Returns:
        List[str]: Sorted list of hostnames running the given service.
    """
    result = run_command(f"ceph orch ps --daemon-type {service_type} --format json")
    daemons = json.loads(result)
    return sorted(set(d["hostname"] for d in daemons))


def compute_expected_rack_mapping(positions_dict: Dict[str, List[str]], ceph_zone_prefix: str) -> Dict[str, str]:
    """
    Compute the expected storage node to rack mapping from the rack placement file.
    Args:
        positions_dict (dict): Rack name to list of node names.
        ceph_zone_prefix (str): Prefix to prepend to rack names.
    Returns:
        Dict[str, str]: Expected mapping of storage node hostnames to rack names.
    """
    expected_mapping: Dict[str, str] = {}
    for rack, nodes in positions_dict.items():
        rack_name = (ceph_zone_prefix + "-" + rack) if ceph_zone_prefix else rack
        for node in nodes:
            if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node):
                expected_mapping[node] = rack_name
    return expected_mapping


def compute_expected_service_nodes(positions_dict: Dict[str, List[str]], sn_count_in_rack: List[int]) -> tuple:
    """
    Compute the expected MON and remaining service (MGR, MDS) node lists
    using the same round-robin logic as service_zoning, without applying changes.
    Args:
        positions_dict (dict): Rack name to list of node names.
        sn_count_in_rack (list): Number of storage nodes per rack.
    Returns:
        tuple: (mon_node_list, remaining_service_node_list)
    """
    number_of_nodes = int(run_command("ceph node ls | jq '.osd | keys | length'"))
    mon_count = 0
    remaining_service_count = 3

    if number_of_nodes in [3, 4]:
        mon_count = 3
    elif number_of_nodes >= 5:
        mon_count = 5
        if number_of_nodes - 2 in sn_count_in_rack:
            mon_count = 3

    service_node_list: List[str] = []
    count = 0
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

    remaining_service_node_list: List[str] = []
    count = 0
    while count < remaining_service_count:
        for nodes in positions_dict.values():
            for node in nodes:
                if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node) and node not in remaining_service_node_list:
                    remaining_service_node_list.append(node)
                    count += 1
                    break
            if count == remaining_service_count:
                break
        if count == remaining_service_count:
            break

    return service_node_list, remaining_service_node_list


def is_zoning_required(positions_dict: Dict[str, List[str]], ceph_zone_prefix: str) -> bool:
    """
    Check if CEPH zoning changes are needed by comparing the current
    CRUSH rack mapping with the expected state.
    If the rack mapping already matches, pool CRUSH rules and service placement
    are expected to match too; any mismatch there is unexpected, so exit with an error.
    Returns:
        bool: True if the rack mapping differs, False if everything matches.
    """
    # Compute expected rack mapping
    expected_rack_mapping = compute_expected_rack_mapping(positions_dict, ceph_zone_prefix)

    # Get current rack mapping
    try:
        current_rack_mapping = get_current_crush_rack_mapping()
    except Exception:
        logger.info("Could not retrieve current CRUSH tree, zoning is required")
        return True

    # Compare rack mappings (only for expected storage nodes)
    for node, expected_rack in expected_rack_mapping.items():
        current_rack = current_rack_mapping.get(node)
        if current_rack != expected_rack:
            logger.info(f"Rack mapping differs for {node}: current={current_rack}, expected={expected_rack}")
            return True

    logger.info("Rack mapping matches expected configuration, verifying CRUSH rules and service placement")

    sn_count_in_rack = []
    for nodes in positions_dict.values():
        sn_count = sum(1 for n in nodes if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", n))
        sn_count_in_rack.append(sn_count)

    try:
        # Retrieve the CRUSH rule ID for the 'replicated rule with rack failure domain' and the list of pools
        rack_rule_id = json.loads(run_command(
            "ceph osd crush rule dump replicated_rule_with_rack_failure_domain --format json"
        ))["rule_id"]
        pools = json.loads(run_command("ceph osd pool ls detail --format json"))


        expected_mon_nodes, expected_remaining_nodes = compute_expected_service_nodes(
            positions_dict, sn_count_in_rack
        )
        # Get current service hosts for MON, MGR, and MDS services
        current_mon_hosts = get_current_service_hosts("mon")
        current_mgr_hosts = get_current_service_hosts("mgr")
        # Check per service, since both MDS services share the daemon type
        current_mds_hosts: Dict[str, List[str]] = {}
        for mds_service in ("mds.admin-tools", "mds.cephfs"):
            result = run_command(f"ceph orch ps --service_name {mds_service} --format json")
            current_mds_hosts[mds_service] = sorted(set(d["hostname"] for d in json.loads(result)))
    except Exception as e:
        logger.error(f"Rack mapping matches expected configuration, but CRUSH rules and service placement could not be verified: {e}")
        logger.error("This is unexpected and needs further investigation")
        sys.exit(1)

    mismatches: List[str] = []

    # Check for any mismatches in service placement and CRUSH rule usage
    pools_without_rack_rule = [p["pool_name"] for p in pools if p.get("crush_rule") != rack_rule_id]
    if pools_without_rack_rule:
        mismatches.append(f"Pools not using rack failure domain CRUSH rule: {pools_without_rack_rule}")

    if sorted(expected_mon_nodes) != current_mon_hosts:
        mismatches.append(f"MON placement differs: current={current_mon_hosts}, expected={sorted(expected_mon_nodes)}")

    if sorted(expected_remaining_nodes) != current_mgr_hosts:
        mismatches.append(f"MGR placement differs: current={current_mgr_hosts}, expected={sorted(expected_remaining_nodes)}")

    for mds_service, mds_hosts in current_mds_hosts.items():
        if sorted(expected_remaining_nodes) != mds_hosts:
            mismatches.append(f"{mds_service} placement differs: current={mds_hosts}, expected={sorted(expected_remaining_nodes)}")

    if mismatches:
        logger.error("Rack mapping matches expected configuration, but the following do not:")
        for mismatch in mismatches:
            logger.error(f"  {mismatch}")
        logger.error("This is unexpected and needs further investigation")
        sys.exit(1)

    logger.info("Current zoning matches expected configuration, no changes needed")
    return False


def create_and_map_racks(positions_dict: Dict[str, List[str]], ceph_zone_prefix: str) -> List[int]:
    """
    Creates Ceph racks corresponding to management racks and maps storage nodes to those racks.
    Args:
        positions_dict (dict): A dictionary mapping rack names to their corresponding
            management node xnames. This information is typically retrieved from
            the rack placement file located at /tmp/rack_info.txt.
        ceph_zone_prefix (str): A prefix to prepend to each rack name when creating the Ceph zones.
    Returns:
        sn_count_in_rack (list): A list representing the number of storage nodes per rack.
            Example format: [1, 2, 1]
    """

    sn_count_in_rack = []

    for rack, nodes in positions_dict.items():
        # Updating the rack or zone prefix
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

def wait_for_ceph_orch(expected_quorum_names) -> bool:
    """
    Wait for Ceph orchestrator operations to complete.
    Checks that all daemons are running, MONs are in quorum
    with the expected quorum names, and cluster health does not
    report monitor-related issues.
    """
    interval = 15
    timeout = 1200
    command_timeout = 60
    deadline = time.monotonic() + timeout
    expected_set = set(expected_quorum_names)
    logger.info("Waiting for ceph orchestrator operations to complete...")

    while True:
        # Commands can hang or fail while MGR fails over / MONs re-elect; retry until the deadline
        try:
            # Check for any non-running ceph daemons
            orch_ps = run_command("ceph orch ps", timeout=command_timeout)
            daemons_transitioning = bool(re.search(r"starting|stopped|error|unknown", orch_ps))
            if daemons_transitioning:
                logger.info("Daemons still transitioning...")

            # Ensure all MONs are in quorum with expected names
            quorum_matched = False
            quorum_status = run_command("ceph quorum_status --format json", timeout=command_timeout)
            try:
                quorum_data = json.loads(quorum_status)
                actual_names = set(quorum_data.get("quorum_names", []))
                if actual_names == expected_set:
                    quorum_matched = True
                else:
                    logger.info(f"Quorum names mismatch: expected {expected_quorum_names}, got {actual_names}")
            except json.JSONDecodeError:
                logger.info("Waiting for MON quorum (invalid JSON response)...")

            # Ensure cluster is not reporting monitor-related health issues
            ceph_health = run_command("ceph health", timeout=command_timeout)
            health_issues = bool(re.search(r"MON_DOWN|MON_LEFT_QUORUM|MON_JOINED_QUORUM", ceph_health))
            if health_issues:
                logger.info("Waiting for monitor health to stabilize...")

            if not daemons_transitioning and quorum_matched and not health_issues:
                logger.info("Ceph orchestrator operations completed successfully.")
                return True
        except (TimeoutError, ValueError) as e:
            logger.info(f"Ceph not responsive yet, retrying: {e}")

        if time.monotonic() >= deadline:
            logger.error("Timed out waiting for ceph orchestrator to finish.")
            return False

        time.sleep(interval)

def service_zoning(positions_dict: Dict[str, List[str]], sn_count_in_rack: List[int]) -> None:
    """
    Perform CEPH services(MON, MGR, MDS) zoning.
    Apply service zoning only if minimum 3 racks with storage nodes (at least one per rack) are present.
    Args:
    positions_dict (dict): A dictionary mapping rack names to their corresponding
        management node xnames. This information is typically retrieved from
        the rack placement file located at /tmp/rack_info.txt.
    sn_count_in_rack (list): A list representing the number of storage nodes per rack.
        Example format: [1, 2, 1]
    Returns:
    None
    """
    service_node_list = []
    remaining_service_node_list = []
    mon_count = 0
    remaining_service_count = 3
    command = "ceph node ls | jq '.osd | keys | length'"
    number_of_nodes = int(run_command(command))

    if len([x for x in sn_count_in_rack if x > 0]) < 3:
        logger.error("Minimum 3 racks with storage nodes are needed for optimal distribution of CEPH data")
        sys.exit(1)

    # We will be modifying monitors count to a maximum of 5, if there are more storage nodes,
    # to provide more fault tolerance.
    # For all the other services, the count will be 3 only.
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

   # Select the storage nodes on which other CEPH services apart from mon are to be run in round robin way across racks
    count = 0
    while count < remaining_service_count:
        for nodes in positions_dict.values():
            for node in nodes:
                if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node) and node not in remaining_service_node_list:
                    remaining_service_node_list.append(node)
                    count += 1
                    break
            if count == remaining_service_count:
                break
        if count == remaining_service_count:
            break

    logger.debug(f"Selected nodes on which CEPH mon service be running: {service_node_list}")
    logger.debug(f"Selected nodes on which remaining CEPH services be running: {remaining_service_node_list}")
    mon_nodes_output = " ".join(service_node_list)
    mon_nodes_count = len(service_node_list)
    remaining_service_nodes_output = " ".join(remaining_service_node_list)
    remaining_service_nodes_count = len(remaining_service_node_list)
    if mon_nodes_count < 1 or remaining_service_nodes_count < 1:
        logger.error("ceph service node list is empty or storage nodes not found")
        sys.exit(1)

    # Apply CEPH monitor service
    logger.info(f"Applying CEPH mon service on nodes {mon_nodes_output}")
    run_command(f"ceph orch apply mon --placement=\"" + str(mon_nodes_count) + " " + mon_nodes_output + "\"")

    # Apply services (MGR, MDS)
    for service in ['mgr', 'mds admin-tools', 'mds cephfs']:
        logger.info(f"Applying {service} service on nodes {remaining_service_nodes_output}")
        run_command(f"ceph orch apply {service} --placement=\"" + str(remaining_service_nodes_count) + " " + remaining_service_nodes_output + "\"")

    time.sleep(30)
    if not wait_for_ceph_orch(service_node_list):
        logger.error("Ceph orchestrator operations for migrating services did not complete successfully within 20 minutes. Please check the cluster status and health to investigate the issue")
        sys.exit(1)


def main() -> None:
    """
    Create ceph zones and map to racks, create and apply ceph CRUSH rule for each rack
    as the failure domain and perform ceph service zoning.
    rack_placement_file is a file with key value pair with xnames of
    racks and corresponding management nodes.
    ceph_prefix is a prefix to prepend to each rack name when creating the Ceph zones.
    """
    if len(sys.argv) not in {2, 3}:
        logger.error("Usage: python ceph_zoning.py <rack_placement_file> [ceph_prefix]")
        sys.exit(1)

    # Load the rack placement file
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as file:
            positions_dict = json.load(file)
    except Exception as e:
        logger.error(f"Failed to load the rack placement file: {e}")
        sys.exit(1)

    ceph_prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    if ceph_prefix:
        logger.info(f"Using ceph prefix: {ceph_prefix}")
    else:
        logger.info("No ceph prefix specified")
    
    # Check if zoning changes are actually needed
    if not is_zoning_required(positions_dict, ceph_prefix):
        logger.info("Skipping CEPH zoning as current configuration already matches expected state")
        return

    # Keep /etc/ceph/ceph.conf current on all storage nodes when MON placement changes
    logger.info("Enabling cephadm management of /etc/ceph/ceph.conf on all hosts")
    run_command("ceph config set mgr mgr/cephadm/manage_etc_ceph_ceph_conf true")

    # Create and map racks, create rules, and perform service zoning
    sn_count_in_rack = create_and_map_racks(positions_dict, ceph_prefix)
    create_and_apply_rules()
    service_zoning(positions_dict, sn_count_in_rack)

if __name__ == "__main__":
    main()
