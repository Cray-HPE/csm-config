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

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

def get_node_rack_missing_quorum(rack_cnt):
    return (rack_cnt - min_rack_cnt)

def validate_master_nodes_placement(placements_dict):
    rack_cnt=1
    master_nodes_cnt=0
    missing_cnt=0
    print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Master nodes"+ bcolors.ENDC)

    # Loop through all the list of racks and corresponding master nodes
    # for master nodes placment validation
    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt) 
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-m00[0-9]$", node):
                # Found master node in a rack
                master_nodes_cnt+=1
                found=1

         if found == 0:
             # Missing master node in a rack
             missing=1
             missing_cnt+=1

         rack_cnt+=1

    print("\nTotal number of master nodes: ", master_nodes_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)

    if master_nodes_cnt >= min_master_node_cnt:
        if rack_cnt == min_rack_cnt and master_nodes_cnt == min_master_node_cnt and  missing_cnt >= node_rack_missing_quorum:
            print(bcolors.FAIL + "\nOne or more management racks missing master node under minimum 3 rack requirement for RR" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the master nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
        elif rack_cnt > min_rack_cnt and master_nodes_cnt >= min_master_node_cnt and missing_cnt > node_rack_missing_quorum:
            print(bcolors.FAIL + "\nMore than one rack missing master node in a", rack_cnt , "rack system" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the master nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
    else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", master_nodes_cnt, "master nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 master nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
        sys.exit(1)

def validate_worker_nodes_placement(placements_dict):
    rack_cnt=1
    worker_nodes_cnt=0
    missing_cnt=0

    print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Worker nodes"+ bcolors.ENDC)

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-w00[0-9]$", node):
                # Found worker node in a rack
                worker_nodes_cnt+=1
                found=1

        if found == 0:
            # Missing worker node in a rack
            missing=1
            missing_cnt+=1

        rack_cnt+=1

    print("\nTotal number of worker nodes: ", worker_nodes_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)

    if worker_nodes_cnt >= min_worker_node_cnt:
        if rack_cnt >= min_rack_cnt and worker_nodes_cnt >= min_worker_node_cnt and  missing_cnt > node_rack_missing_quorum:
            if rack_cnt == min_rack_cnt and worker_nodes_cnt == min_worker_node_cnt
                print(bcolors.FAIL + "\nOne or more racks missing worker node under minimum 3 rack condition" + bcolors.ENDC)
                print(bcolors.FAIL + "\nPlease re arrange the worker nodes for equal distribution" + bcolors.ENDC)
                print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            elif rack_cnt > min_rack_cnt and worker_nodes_cnt >= min_worker_node_cnt
                print(bcolors.FAIL + "\nMore than one rack missing worker node in a", rack_cnt , "rack system" + bcolors.ENDC)
                print(bcolors.FAIL + "\nPlease re arrange the worker nodes for equal distribution" + bcolors.ENDC)
                print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
    else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", worker_nodes_cnt, "worker nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 worker nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
        sys.exit(1)

def validate_ceph_nodes_placement(placements_dict):
    rack_cnt=1
    storage_nodes_cnt=0
    missing_cnt=0

    print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Storage (CEPH) nodes"+ bcolors.ENDC)

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*ncn-s00[0-9]$", node):
                # Found storage node in a rack
                storage_nodes_cnt+=1
                found=1

        if found == 0:
            # Missing storage node in a rack
            missing=1
            missing_cnt+=1

        rack_cnt+=1

    print("\nTotal number of storage nodes: ", storage_nodes_cnt)

    node_rack_missing_quorum=get_node_rack_missing_quorum(rack_cnt)

    if storage_nodes_cnt >= min_storage_node_cnt:
        if rack_cnt == min_rack_cnt and storage_nodes_cnt == min_master_node_cnt and  node_rack_missing_quorum >= node_rack_missing_quorum:
            print(bcolors.FAIL + "\nOne or more racks missing storage node under minimum 3 rack condition" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the storage nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
        elif rack_cnt > min_rack_cnt and storage_nodes_cnt >= min_master_node_cnt and node_rack_missing_quorum > node_rack_missing_quorum:
            print(bcolors.FAIL + "\nMore than one rack missing storage node in a", rack_cnt , "rack system" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the storage nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
     else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", storage_nodes_cnt, "storage nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 storage nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
        sys.exit(1)

def validate_compute_uan_nodes_placement(placements_dict):
    rack_cnt=1
    managed_nodes_cnt=0
    missing_cnt=0

    print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Managed nodes (Compute and UANs)"+ bcolors.ENDC)

    for rack_cnt, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_cnt)
        print("Rack ID: ", rack_id)
        print("Management/ Managed Nodes: ", nodes)

        found=0
        for node in nodes:
            if re.match(r"^.*nid00000[0-9]$", node) or re.match(r"^.*uan0[0-9]$", node):
                print(bcolors.WARNING + "Found", node, "Compute/ UAN node under management rack" + bcolors.ENDC)
                managed_nodes_cnt+=1
                found=1

        if found == 1:
            print(bcolors.WARNING +  "\nOne or more Managed nodes found under management Racks" + bcolors.ENDC)

        rack_cnt+=1

    print("\nTotal number of racks: ", rack_cnt)

    if managed_nodes_cnt == 0:
        print(bcolors.OKGREEN + "\nTotal", managed_nodes_cnt, "number of Managed nodes found under Management racks" + bcolors.ENDC)
    else:
        print(bcolors.WARNING + "\nTotal", managed_nodes_cnt, "number of Managed nodes found under  Management racks" + bcolors.ENDC)

def main():
    if len(sys.argv) != 2:
        print("Usage: python rr_placement_validation.py <mgmt_nodes_placement_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        mgmt_placements = file.read()

    placements_dict = json.loads(mgmt_placements)

    print(bcolors.OKGREEN + bcolors.UNDERLINE +"\n## Validate Management nodes placement ##" + bcolors.ENDC)

    ## RR can not be supported with < 3 racks (mainly to support RR for CEPH utility storage).
    ## Fail the validation if the condition is not met.
    num_racks = len(placements_dict)
    if num_racks <= 2:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", num_racks, "racks" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 managment racks configured" + bcolors.ENDC)
        print(bcolors.FAIL + "\nExiting mgmt nodes placement validation...\n"  + bcolors.ENDC)
        sys.exit(1)

    # Do master nodes placement validation
    validate_master_nodes_placement(placements_dict)

    # Do worker nodes placement validation
    validate_worker_nodes_placement(placements_dict)

    # Do storge nodes (Utility storage/ CEPH) placement validation
    validate_ceph_nodes_placement(placements_dict)
   
    print(bcolors.OKGREEN + "\nManagment nodes placement validation suceeded..." + bcolors.ENDC)

    # Do managed nodes (compute and UAN) placement validation: Just WARN if they are 
    # placed under any management rack
    validate_compute_uan_nodes_placement(placements_dict)

if __name__ == "__main__":
    main()
