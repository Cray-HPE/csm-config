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
import logging

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

logging.basicConfig(filename="/tmp/rr_mgmt_placment_validation.log",
					format='%(asctime)s %(message)s',
					filemode='w')

logger=logging.getLogger()

logger.setLevel(logging.DEBUG)

#logger.debug("This is just a harmless debug message") 
#logger.info("This is just an information for you") 
#logger.warning("OOPS!!!Its a Warning") 
#logger.error("Have you try to divide a number by zero") 
#logger.critical("The Internet is not working....")

def  validate_master_nodes_placement(placements_dict):
     rack_num=1
     master_nodes_cnt=0
     missing_cnt=0
     print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Master nodes"+ bcolors.ENDC)

     for rack_num, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_num) 
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            #print(node)
            if re.match(r"^.*ncn-m00[0-9]$", node):
                print(bcolors.OKGREEN + "Found", node, "master node" + bcolors.ENDC)
                master_nodes_cnt+=1
                found=1

        if found == 0:
            print(bcolors.WARNING +  "Missing master node" + bcolors.ENDC)
            missing=1
            missing_cnt+=1

        rack_num+=1
     print("\nTotal number of master nodes: ", master_nodes_cnt)

     if master_nodes_cnt >= 3:
        if rack_num == 3 and master_nodes_cnt == 3 and  missing_cnt >= 1:
            print(bcolors.FAIL + "\nOne or more racks missing master node under minimum 3 rack condition met" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the master nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
        elif rack_num > 3 and master_nodes_cnt >= 3 and missing_cnt > 1:
            print(bcolors.FAIL + "\nMore than one rack missing master node in a",rack_num, "rack system" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the master nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            #sys.exit(1)
     else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", master_nodes_cnt, "master nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 master nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)


def validate_worker_nodes_placement(placements_dict):
     rack_num=1
     worker_nodes_cnt=0
     missing_cnt=0
     print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Worker nodes"+ bcolors.ENDC)

     for rack_num, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_num)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            #print(node)
            if re.match(r"^.*ncn-w00[0-9]$", node):
                print(bcolors.OKGREEN + "Found", node, "worker node" + bcolors.ENDC)
                worker_nodes_cnt+=1
                found=1

        if found == 0:
            print(bcolors.WARNING +  "Missing worker node" + bcolors.ENDC)
            missing=1
            missing_cnt+=1

        rack_num+=1
     print("\nTotal number of worker nodes: ", worker_nodes_cnt)

     if worker_nodes_cnt >= 3:
        if rack_num == 3 and worker_nodes_cnt == 3 and  missing_cnt >= 1:
            print(bcolors.FAIL + "\nOne or more racks missing worker node under minimum 3 rack condition met" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the worker nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
        elif rack_num > 3 and worker_nodes_cnt >= 3 and missing_cnt > 1:
            print(bcolors.FAIL + "\nMore than one rack missing worker node in a",rack_num, "rack system" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the worker nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            #sys.exit(1)
     else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", worker_nodes_cnt, "worker nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 worker nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)

def validate_ceph_nodes_placement(placements_dict):
     rack_num=1
     storage_nodes_cnt=0
     missing_cnt=0
     print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Management Storage (CEPH) nodes"+ bcolors.ENDC)

     for rack_num, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_num)
        print("Rack ID: ", rack_id)
        print("Management Nodes: ", nodes)

        found=0
        for node in nodes:
            #print(node)
            if re.match(r"^.*ncn-s00[0-9]$", node):
                print(bcolors.OKGREEN + "Found", node, "storage node" + bcolors.ENDC)
                storage_nodes_cnt+=1
                found=1

        if found == 0:
            print(bcolors.WARNING +  "Missing storage node" + bcolors.ENDC)
            missing=1
            missing_cnt+=1

        rack_num+=1
     print("\nTotal number of storage nodes: ", storage_nodes_cnt)

     if storage_nodes_cnt >= 3:
        if rack_num == 3 and storage_nodes_cnt == 3 and  missing_cnt >= 1:
            print(bcolors.FAIL + "\nOne or more racks missing storage node under minimum 3 rack condition met" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the storage nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            sys.exit(1)
        elif rack_num > 3 and storage_nodes_cnt >= 3 and missing_cnt > 1:
            print(bcolors.FAIL + "\nMore than one rack missing storage node in a",rack_num, "rack system" + bcolors.ENDC)
            print(bcolors.FAIL + "\nPlease re arrange the storage nodes for equal distribution" + bcolors.ENDC)
            print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
            #sys.exit(1)
     else:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", storage_nodes_cnt, "storage nodes" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 storage nodes configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)


def validate_compute_uan_nodes_placement(placements_dict):
     rack_num=1
     managed_nodes_cnt=0
     missing_cnt=0
     print(bcolors.OKGREEN + bcolors.UNDERLINE + "\nValidate Managed nodes (Compute and UANs)"+ bcolors.ENDC)

     for rack_num, (rack_id, nodes) in enumerate(placements_dict.items()):
        print("\nRack number: ", rack_num)
        print("Rack ID: ", rack_id)
        print("Management/ Managed Nodes: ", nodes)

        found=0
        for node in nodes:
            #print(node)
            if re.match(r"^.*nid00000[0-9]$", node) or re.match(r"^.*uan0[0-9]$", node):
                print(bcolors.OKGREEN + "Found", node, "Compute/ UAN node" + bcolors.ENDC)
                managed_nodes_cnt+=1
                found=1

        if found == 1:
            print(bcolors.WARNING +  "\nOne or more Managed nodes found under management Racks" + bcolors.ENDC)

        rack_num+=1

     if managed_nodes_cnt == 0:
        print(bcolors.OKGREEN + "\nTotal", managed_nodes_cnt, "number of Managed nodes found under Management racks" + bcolors.ENDC)
     else:
        print(bcolors.WARNING + "\nTotal", managed_nodes_cnt, "number of Managed nodes found under  Management racks" + bcolors.ENDC)

#def log_placement_validaion_report():

def main():
    if len(sys.argv) != 2:
        print("Usage: python rr_placement_validation.py <placement_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        mgmt_placements = file.read()
    #print(mgmt_placements)
    placements_dict = json.loads(mgmt_placements)

    # Validate management nodes (MNs, WNs and SNs) placement validation
    print(bcolors.OKGREEN + bcolors.UNDERLINE +"\n## Validate Management nodes placement ##" + bcolors.ENDC)

    # validate number of management racks for RR
    num_racks = len(placements_dict)

    print("\nTotal number of management racks: ", num_racks)

    ## RR can not be supported with < 3 racks (mainly to support RR for CEPH storage)
    ## Fail the validation if the condition is not met
    if num_racks <= 2:
        print(bcolors.FAIL + "\nRack Resiliency can not be enabled with", num_racks, "racks" + bcolors.ENDC)
        print(bcolors.FAIL + "\nNeed minimum of 3 managment racks configured" + bcolors.ENDC)
        print(bcolors.FAIL + "Exiting placement validation...\n"  + bcolors.ENDC)
        sys.exit(1)

    # Master nodes placement validation
    validate_master_nodes_placement(placements_dict)

    # Worker nodes placement validation
    validate_worker_nodes_placement(placements_dict)

    # CEPH (placement) nodes placement validation
    validate_ceph_nodes_placement(placements_dict)
   
    print(bcolors.OKGREEN + "\nManagment nodes placement validation suceeded..." + bcolors.ENDC)

    # WARN compute and UAN nodes placement under management nodes racks
    validate_compute_uan_nodes_placement(placements_dict)

    # Log report 
    #log_placement_validaion_report()

if __name__ == "__main__":
    main()
