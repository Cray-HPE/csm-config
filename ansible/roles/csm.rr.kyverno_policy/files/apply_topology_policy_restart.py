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

def apply_kyverno_policy(yaml_file):
    try:
        subprocess.run(["kubectl", "apply", "-f", yaml_file], check=True)
        print(f"Successfully applied kyverno topology policy from {yaml_file}")
    except subprocess.CalledProcessError:
        print(f"Unable to apply Kyverno topology policy")
        sys.exit(1)

def load_configmap(name, namespace):
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

def rollout_restart_critical_services(config):
    critical_services_json = config['data']['critical-service-config.json']
    critical_services = json.loads(critical_services_json)['critical_services']

    for name, details in critical_services.items():
        resource_type = details["type"].lower()
        namespace = details["namespace"]
        command = ["kubectl", "rollout", "restart", f"{resource_type}/{name}", "-n", namespace]

        try:
            subprocess.run(command, check=True)
            print(f"Restarted {resource_type}/{name} in namespace {namespace}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart {resource_type}/{name} in namespace {namespace}")
            print(f"Error: {e.stderr}")
            sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: apply_topology_policy_restart.py <kyverno-policy.yaml>")
        sys.exit(1)

    kyverno_policy_file = sys.argv[1]

    apply_kyverno_policy(kyverno_policy_file)
    config = load_configmap("rrs-mon-static", "rack-resiliency")
    rollout_restart_critical_services(config)

if __name__ == "__main__":
    main()
