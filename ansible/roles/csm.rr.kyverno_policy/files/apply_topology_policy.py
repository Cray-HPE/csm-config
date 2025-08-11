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
Apply RR ClusterPolicy and do rollout restart of the critical services defined
in RR static ConfigMap.
"""

import yaml
import json
import subprocess
import sys
import tempfile
import os

def load_configmap(name, namespace):
    """
    Fetch and return a ConfigMap from the specified namespace as a JSON object.
    Args:
        name (str): Name of the ConfigMap.
        namespace (str): Kubernetes namespace of the ConfigMap.
    Returns:
        dict: Parsed JSON of the ConfigMap contents.
    """
    try:
        result = subprocess.run(
            ["kubectl", "get", "configmap", name, "-n", namespace, "-o", "json"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch ConfigMap '{name}' from namespace '{namespace}'")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def update_policy_with_services(policy_path, service_names):
    """
    Load a Kyverno policy YAML file, and update its match.resources.names field 
    with the provided list of service names.
    Args:
        policy_path (str): Path to the static Kyverno policy YAML file.
        service_names (list): List of critical service names to insert into the policy.
    Returns:
        dict: Updated Kyverno policy as a Python dictionary.
    """
    with open(policy_path, "r") as f:
        policy = yaml.safe_load(f)

    rules = policy.get("spec", {}).get("rules", [])
    target_rule = None

    # Find the rule named 'insert-rack-res-label'
    for rule in rules:
        if rule.get("name") == "insert-rack-res-label":
            target_rule = rule
            break

    if not target_rule:
        print("No rule named 'insert-rack-res-label' found in the policy.")
        sys.exit(1)

    # Navigate to the location where names need to be updated
    try:
        match_resources = target_rule["match"]["any"][0]["resources"]
        match_resources["names"] = service_names
    except (KeyError, IndexError) as e:
        print("Failed to update policy with resource names. Invalid policy structure.")
        print(f"Error: {e}")
        sys.exit(1)

    return policy


def apply_kyverno_policy(policy_dict):
    """
    Apply the given Kyverno policy by writing it to a temporary file and using kubectl apply.
    Args:
        policy_dict (dict): Kyverno policy represented as a Python dictionary.
    """
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".yaml", delete=False) as temp_file:
        yaml.dump(policy_dict, temp_file)
        temp_file_path = temp_file.name

    try:
        subprocess.run(["kubectl", "apply", "-f", temp_file_path], check=True)
        print(f"Successfully applied Kyverno policy from generated YAML")
    except subprocess.CalledProcessError:
        print("Unable to apply Kyverno topology policy")
        os.remove(temp_file_path)
        sys.exit(1)

    os.remove(temp_file_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: apply_topology_policy_restart.py <kyverno-policy.yaml>")
        sys.exit(1)

    policy_path = sys.argv[1]

    # Load critical services
    config = load_configmap("rrs-mon-static", "rack-resiliency")
    try:
        critical_services_json = config['data']['critical-service-config.json']
        critical_services = json.loads(critical_services_json)['critical_services']
    except KeyError as e:
        print(f"Missing expected key in ConfigMap: {e}")
        sys.exit(1)

    # Extract critical services names
    service_names = list(critical_services.keys())

    # Update policy with names and apply
    updated_policy = update_policy_with_services(policy_path, service_names)
    apply_kyverno_policy(updated_policy)

if __name__ == "__main__":
    main()
