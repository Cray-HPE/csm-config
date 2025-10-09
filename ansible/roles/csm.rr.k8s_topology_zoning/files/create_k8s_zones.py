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

import subprocess
import json
import sys
from typing import Dict, List

def get_rack_info() -> Dict[str, List[str]]:
    """
    Get key value pair of rack(s) and corresponding management nodes (xnames) fetched
    from the placement file /tmp/rack_info.txt.
    Return rack_info(key value pair of rack(s) and corresponding management nodes (xnames)).
    """

    # To get the rack to node mapping details by executing "rack_to_node_mapping.py"
    try:
        # Fix ansible error for failing to invoke "rack_to_node_mapping.py"
        # For now using "/tmp/rack_info.txt" produced from discovery to make CFS ansible play work
        #result = subprocess.run(["python3", "rack_to_node_mapping.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        result = subprocess.run(["cat", "/tmp/rack_info.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running kubectl: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
    print(f"Result: {result}")
    rack_info = result.stdout
    rack_info = json.loads(rack_info)
    return rack_info

def generate_node_zone_mapping(rack_info: Dict[str, List[str]], k8s_zone_prefix: str) -> None:
    """
    Generate node to zone mapping for k8s topology zone labels to management racks 
    with corresponding master and worker nodes.
    Here zone name(rack_id) is: k8s_zone_prefix + xname of the rack
    Store the mapping in a file for Ansible to process.
    """
    node_zone_mapping = {}
    
    # To traverse the nodes in the rack and build the mapping
    for rack_id, nodes in rack_info.items():
        zone_name = rack_id
        if k8s_zone_prefix:
            zone_name = k8s_zone_prefix + "-" + rack_id
        
        for node in nodes:
            if not node.startswith("ncn-s"):
                print(f"Node {node} will be placed on {zone_name}")
                node_zone_mapping[node] = zone_name
    
    # Write the node-zone mapping to a file for Ansible to process
    output_file = "/tmp/k8s_node_zone_mapping.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(node_zone_mapping, f, indent=2)
    
    print(f"Node to zone mapping saved to {output_file}")
    print(f"Total nodes to be labeled: {len(node_zone_mapping)}")

def main() -> None:
    """
    Apply k8s topology zones to management racks with corresponding master and worker nodes.
    rack_info here is a key value pair of rack(s) and corresponding management nodes (xnames) fetched
    from the placement file /tmp/rack_info.txt.
    k8s_zone_prefix is passed as command line argument from Ansible.
    """
    # Check if k8s_zone_prefix is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: create_k8s_zones.py <k8s_zone_prefix>")
        sys.exit(1)
    
    k8s_zone_prefix = sys.argv[1]
    
    # To get the rack info
    rack_info = get_rack_info()
    # Generate the node-zone mapping for Ansible to process
    generate_node_zone_mapping(rack_info, k8s_zone_prefix)

if __name__ == "__main__":
    main()
