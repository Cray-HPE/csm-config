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
import base64

def get_k8s_zone_prefix():
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

    print(f"Decoded YAML saved to {output_file}")

    # Define the key path
    output_file = "/tmp/customizations1.yaml"
    k8s_key_path = "spec.kubernetes.services.k8s_zone_prefix"
    
    # Run yq command to extract the value
    k8s_yq_cmd = ["yq", "r", output_file, k8s_key_path]
    k8s_zone = subprocess.run(k8s_yq_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

    # Extract and clean the output
    k8s_zone_prefix = k8s_zone.stdout.strip()
    return k8s_zone_prefix

def get_rack_info():
    # To get the rack to node mapping details by executing "rack_to_node_mapping.py"
    try:
        # Fix ansible error for failing to invoke "rack_to_node_mapping.py" 
        # For now using "/tmp/rack_info.txt" produced from discovery to make CFS ansible play work
        #result = subprocess.run(["python3", "rack_to_node_mapping.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        result = subprocess.run(["cat", "/tmp/rack_info.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running kubectl: {e.stderr}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        exit(1)
    print(f"Result: {result}")
    rack_info = result.stdout
    rack_info = json.loads(rack_info)
    return rack_info

def label_nodes(rack_info):
    # To traverse the nodes in the rack and assign them the labels
    for rack_id, nodes in rack_info.items():
        k8s_zone_prefix = get_k8s_zone_prefix(
        if k8s_zone_prefix:
            rack_id = k8s_zone_prefix + "-" + rack_id
        for node in nodes:
            if not node.startswith("ncn-s"):
                print(f"Node {node} is going to be placed on zone-{rack_id}")
                result = subprocess.run(
                        ["kubectl", "label", "node", f"{node}", f"topology.kubernetes.io/zone=rack-{rack_id}", "--overwrite"],
                       stdout=subprocess.PIPE
                        )

def main():
    # To get the rack info
    rack_info = get_rack_info()
    # To label the rack nodes
    label_nodes(rack_info)

if __name__ == "__main__":
    main()
