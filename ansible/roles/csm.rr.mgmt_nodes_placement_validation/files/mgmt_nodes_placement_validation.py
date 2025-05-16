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

import json
import subprocess
import re
import sys

min_rack_cnt = 3
min_master_node_cnt = 3
min_worker_node_cnt = 3
min_storage_node_cnt = 3

def get_node_rack_missing_quorum(rack_cnt):
    return (rack_cnt - min_rack_cnt)

def validate_master_nodes_placement(placements_dict):
    rack_cnt=1
    master_nodes_cnt=0
    missing_cnt=0
    print("\nValidate Management Master nodes")

    # Loop through all the list of racks and corresponding master nodes
    # for master nodes placment validation
    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-m[0-9][0-9][0-9]$", node):
                # Found master node in a rack
                print("\nFound master node", node, "in a rack",rack_id)
                master_nodes_cnt+=1
                found=1

        if found == 0:
            # Missing master node in a rack
            print("Missing master node in a rack", rack_id)
            missing=1
            missing_cnt+=1

        rack_cnt+=1

    print("\nTotal number of master nodes: ", master_nodes_cnt)
    print("\nTotal number of racks: ",rack_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)
    print("\nnode_rack_missing_quorum",node_rack_missing_quorum)

    if master_nodes_cnt >= min_master_node_cnt:
        if rack_cnt == min_rack_cnt and master_nodes_cnt == min_master_node_cnt and  missing_cnt > node_rack_missing_quorum:
            print("\nOne or more management racks missing master node under minimum 3 rack requirement for RR")
            print("\nPlease re arrange the master nodes for equal distribution")
            print("Exiting placement validation...\n")
            sys.exit(1)
        elif (rack_cnt > min_rack_cnt) and (master_nodes_cnt >= min_master_node_cnt) and (missing_cnt > node_rack_missing_quorum):
            print("\nMore than one rack missing master node in a", rack_cnt , "rack system")
            print("\nPlease re arrange the master nodes for equal distribution")
            print("Exiting placement validation...\n")
            sys.exit(1)
    else:
        print("\nRack Resiliency can not be enabled with", master_nodes_cnt, "master nodes")
        print("\nNeed minimum of 3 master nodes configured")
        print("Exiting placement validation...\n")
        sys.exit(1)

def validate_worker_nodes_placement(placements_dict):
    rack_cnt=1
    worker_nodes_cnt=0
    missing_cnt=0

    print("\nValidate Management Worker nodes")

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-w[0-9][0-9][0-9]$", node):
                # Found worker node in a rack
                print("\nFound worker node", node, "in a rack",rack_id)
                worker_nodes_cnt+=1
                found=1

        if found == 0:
            # Missing worker node in a rack
            print("Missing worker node in a rack", rack_id)
            missing=1
            missing_cnt+=1

        rack_cnt+=1

    print("\nTotal number of worker nodes: ", worker_nodes_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)
    print("\nnode_rack_missing_quorum",node_rack_missing_quorum)

    if worker_nodes_cnt >= min_worker_node_cnt:
        if rack_cnt >= min_rack_cnt and worker_nodes_cnt >= min_worker_node_cnt and  missing_cnt > node_rack_missing_quorum:
            if rack_cnt == min_rack_cnt and (worker_nodes_cnt == min_worker_node_cnt):
                print("\nOne or more racks missing worker node under minimum 3 rack condition")
                print("\nPlease re arrange the worker nodes for equal distribution")
                print("Exiting placement validation...\n")
                sys.exit(1)
            elif rack_cnt > min_rack_cnt and (worker_nodes_cnt >= min_worker_node_cnt):
                print("\nMore than one rack missing worker node in a", rack_cnt , "rack system")
                print("\nPlease re arrange the worker nodes for equal distribution")
                print("Exiting placement validation...\n")
                sys.exit(1)
    else:
        print("\nRack Resiliency can not be enabled with", worker_nodes_cnt, "worker nodes")
        print("\nNeed minimum of 3 worker nodes configured")
        print("Exiting placement validation...\n")
        sys.exit(1)

def validate_ceph_nodes_placement(placements_dict):
    rack_cnt=1
    storage_nodes_cnt=0
    missing_cnt=0

    print("\nValidate Management Storage (CEPH) nodes")

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-s[0-9][0-9][0-9]$", node):
                # Found storage node in a rack
                print("\nFound storage node", node, "in a rack",rack_id)
                storage_nodes_cnt+=1
                found=1

        if found == 0:
            # Missing storage node in a rack
            print("Missing storage node in a rack", rack_id)
            missing=1
            missing_cnt+=1

        rack_cnt+=1

    print("\nTotal number of storage nodes: ", storage_nodes_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)

    if storage_nodes_cnt >= min_storage_node_cnt:
        if rack_cnt == min_rack_cnt and storage_nodes_cnt == min_master_node_cnt and  missing_cnt > node_rack_missing_quorum:
            print("\nOne or more racks missing storage node under minimum 3 rack condition")
            print("\nPlease re arrange the storage nodes for equal distribution")
            print("Exiting placement validation...\n")
            sys.exit(1)
        elif rack_cnt > min_rack_cnt and storage_nodes_cnt >= min_master_node_cnt and missing_cnt > node_rack_missing_quorum:
            print("\nMore than one rack missing storage node in a", rack_cnt , "rack system")
            print("\nPlease re arrange the storage nodes for equal distribution")
            print("Exiting placement validation...\n")
            sys.exit(1)
    else:
        print("\nRack Resiliency can not be enabled with", storage_nodes_cnt, "storage nodes")
        print("\nNeed minimum of 3 storage nodes configured")
        print("Exiting placement validation...\n")
        sys.exit(1)

def validate_compute_uan_nodes_placement(placements_dict):
    rack_cnt=1
    managed_nodes_cnt=0
    missing_cnt=0

    print("\nValidate Managed nodes (Compute and UANs)")

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management/ Managed Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*nid[0-9][0-9][0-9][0-9][0-9][0-9]$", node) or re.match(r"^.*uan[0-9][0-9]$", node):
                print("Found", node, "Compute/ UAN node under management rack:", rack_id)
                managed_nodes_cnt+=1
                found=1

        rack_cnt+=1

    if found == 1:
        print("\nOne or more Managed nodes found under management Racks")

    print("\nTotal number of racks: ", rack_cnt)

    if managed_nodes_cnt == 0:
        print("\nTotal", managed_nodes_cnt, "number of Managed nodes found under Management racks")
    else:
        print("\nTotal", managed_nodes_cnt, "number of Managed nodes found under  Management racks")

def main():
    if len(sys.argv) != 2:
        print("Usage: python rr_placement_validation.py <mgmt_nodes_placement_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        mgmt_placements = file.read()

    placements_dict = json.loads(mgmt_placements)

    print("\n## Validate Management nodes placement ##")

    ## RR can not be supported with < 3 racks (mainly to support RR for CEPH utility storage).
    ## Fail the validation if the condition is not met.
    num_racks = len(placements_dict)
    if num_racks <= 2:
        print("\nRack Resiliency can not be enabled with", num_racks, "racks")
        print("\nNeed minimum of 3 managment racks configured")
        print("\nExiting mgmt nodes placement validation...\n")
        sys.exit(1)

    # Do master nodes placement validation
    validate_master_nodes_placement(placements_dict)

    # Do worker nodes placement validation
    validate_worker_nodes_placement(placements_dict)

    # Do storge nodes (Utility storage/ CEPH) placement validation
    validate_ceph_nodes_placement(placements_dict)
   
    print("\nManagment nodes placement validation suceeded...")

    # Do managed nodes (compute and UAN) placement validation: Just WARN if they are 
    # placed under any management rack
    validate_compute_uan_nodes_placement(placements_dict)

if __name__ == "__main__":
    main()
