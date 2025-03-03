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

sn_count_in_rack = []
def create_and_map_racks(positions_dict):
    global sn_count_in_rack
    #Create buckets for racks and add them to the hierarchy under root=default
    for racknum, (rack, nodes) in enumerate(positions_dict.items()):    
        command1 = "ceph osd crush add-bucket "+rack+" rack"
        print(command1)
        result = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        print('Result for add-bucket command', result.returncode)
        print('Output for add-bucket command', result.stdout)
    
        command2 = "ceph osd crush move "+rack+" root=default"
        print(command2)
        result = subprocess.run(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        print('Result for crush move command', result.returncode)
        print('Output for crush move command', result.stdout)
    
        #Move the storage hosts to the rack based on the discovered placement obtained from the input file
        print(nodes)
        sn_count = 0
        for node in nodes:
            print(node)
            if re.match(r"^.*ncn-s00[0-9]$", node):
                print("Node is storage node")
                sn_count = sn_count + 1
                command3="ceph osd crush move "+node+" rack="+rack
                print(command3)
                result = subprocess.run(command3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
                print('Result for crush move command', result.returncode)
                print('Output for crush move command', result.stdout)
        sn_count_in_rack.append(sn_count)
    print("storage node count list is ", sn_count_in_rack)

def create_and_apply_rules():
    #Create a CRUSH rule with Rack as the failure domain
    command4="ceph osd crush rule create-replicated replicated_rule_with_rack_failure_domain default rack"
    print(command4)
    result = subprocess.run(command4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for rule creation command', result.returncode)
    print('Output for rule creation command', result.stdout)

    #Apply the above created rule to the CEPH pools
    command5="ceph osd pool ls"
    print(command5)
    result = subprocess.run(command5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for pool listing command', result.returncode)
    ceph_pools = result.stdout.splitlines()
    print('Output for pool listing command', ceph_pools)
    for pool in ceph_pools:
        print(pool)
        command6="ceph osd pool set "+pool+" crush_rule replicated_rule_with_rack_failure_domain"
        print(command6)
        result = subprocess.run(command6, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        print('Result for pool setting with rule command', result.returncode)
        print('Output for pool setting with rule command', result.stdout)

# Distributes CEPH services across racks so CEPH will be intact in case of rack failures
# The service count would be either 3 or 5 depending on the number of storage nodes and also their distribution
def service_zoning(positions_dict):
    global sn_count_in_rack
                                                                                        
    service_node_list = []
    count = 0
    command = "craysys metadata get num_storage_nodes"
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for storage node count command', result.returncode)
    number_of_nodes = int(result.stdout)
    number_of_nodes = 5
    print('Output for storage node count command', number_of_nodes)
   
    if len([x for x in sn_count_in_rack if x > 0]) < 3:
        print('WARNING: Minimum 3 racks with storage nodes to be available for optimal distribution of CEPH data and services. Without that rack resiliency would not be gauranteed')

    if number_of_nodes == 3 or number_of_nodes == 4:
        mon_count = 3
    elif number_of_nodes >= 5:
        mon_count = 5
        # Incase of 5 monitors, there should be atleast 3 monitors to be running for establishing quorum.
        # But if 3 mons are on same rack, there is a chance that CEPH would not be functional when that particular rack goes down.
        # So configuring only 3 monitors each on one rack to handle the above scenario.
        if number_of_nodes-2 in sn_count_in_rack:
            mon_count = 3
        
    print('mon count is :', mon_count)

    # Select the storage nodes on which the services are to be run in round robin way across racks
    while count <= mon_count:
        for racknum, (rack, nodes) in enumerate(positions_dict.items()):

                                                                                                  
            print(nodes)

            for node in nodes:
                print(node)
                if re.match(r"^.*ncn-s00[0-9]$", node):
                    print("Node is storage node")
                    if node not in service_node_list:
                        service_node_list.append(node)
                        count=count+1
                        break
            if count == mon_count:
                break
        if count == mon_count:
            break

    print(service_node_list)
    nodes_output = " ".join(service_node_list)
    nodes_count = len(service_node_list)


    command = "ceph orch apply mon --placement=\"" + str(nodes_count) + " " + nodes_output + "\""
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for mon placement command', result.returncode)

    command = "ceph orch apply mgr --placement=\"" + str(nodes_count) + " " + nodes_output + "\""
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for mgr placement command', result.returncode)

    command = "ceph orch apply mds admin-tools --placement=\"" + str(nodes_count) + " " + nodes_output + "\""
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for admin-tools mds placement command', result.returncode)

    command = "ceph orch apply mds cephfs --placement=\"" + str(nodes_count) + " " + nodes_output + "\""
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    print('Result for cephfs mds placement command', result.returncode)



def main():
    if len(sys.argv) != 2:
        print("Usage: python ceph_zoning.py <rack_placement file>")
        sys.exit(1)
    
    #Obtain the placement file as an input and load the JSON data
    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        positions = file.read()
    #positions = '{"x3000":["ncn-m001","ncn-w001","ncn-w004","ncn-w007","ncn-s001"],"x3001":["ncn-m002","ncn-w002","ncn-w006","ncn-s003"],"x3002":["ncn-m003","ncn-w003","ncn-w009","ncn-b005","ncn-s002"]}'
    print(positions)
    positions_dict = json.loads(positions)
    
    # Create buckets for rack and map hosts to racks
    create_and_map_racks(positions_dict)
                                          
    # Create CRUSH rule and apply it to pools
    create_and_apply_rules()
    
    # Perform CEPH services zoning 
    service_zoning(positions_dict)

if __name__ == "__main__":
    main()

