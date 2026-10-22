#!/usr/bin/python3
#
# MIT License
#
# (C) Copyright 2026 Hewlett Packard Enterprise Development LP
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
This script updates Ceph monitor information in Kubernetes ConfigMaps after Ceph service zoning changes.
"""

import json
import logging
import subprocess
from typing import List

# Set up logger
logger = logging.getLogger("UpdateCephConfigMaps")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def run_command(command: str) -> str:
    """
    Helper function to run a shell command.
    Args:
        command (str): The shell command to run.
    Returns:
        str: The output of the command.
    """
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, shell=True, check=True, timeout=300
        )
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"Command timed out: {command}") from e
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Command {command} errored out with: {e.stderr}") from e
    return result.stdout

def get_new_monitors() -> List[str]:
    """Get the current list of Ceph monitor addresses from the monitor map."""
    result = run_command("ceph mon dump -f json")
    mon_dump = json.loads(result)
    return [mon["public_addr"].split("/")[0] for mon in mon_dump["mons"]]

def check_configmap_exists(namespace: str, name: str) -> bool:
    """Return True if the ConfigMap exists; raise on any kubectl/API error."""
    return bool(run_command(
        f"kubectl -n {namespace} get cm {name} --ignore-not-found -o name"
    ).strip())

def update_ceph_csi_configmaps() -> None:
    """
    Update the monitors list in all Ceph CSI ConfigMaps across relevant
    namespaces using the current Ceph monitor map.
    """
    new_monitors = get_new_monitors()
    logger.info(f"New monitor list: {new_monitors}")

    # Namespaces ceph-rbd, ceph-cephfs, default, services contain ceph-csi-config configmap
    for ns in ["ceph-rbd", "ceph-cephfs", "default", "services"]:
        if not check_configmap_exists(ns, "ceph-csi-config"):
            logger.info(f"Skipping {ns} (ceph-csi-config not found)")
            continue
        logger.info(f"Updating ceph-csi-config in namespace {ns}")
        result = run_command(f"kubectl -n {ns} get cm ceph-csi-config -o json")
        cm = json.loads(result)

        config = json.loads(cm.get("data", {}).get("config.json", "[]"))
        changed = False
        for entry in config:
            current_monitors = entry.get("monitors", [])
            if sorted(current_monitors) != sorted(new_monitors):
                entry["monitors"] = new_monitors
                changed = True

        if not changed:
            logger.info(f"No monitor change detected in namespace {ns}, skipping update")
            continue
        cm["data"]["config.json"] = json.dumps(config)

        subprocess.run(
            ["kubectl", "apply", "-f", "-"],
            input=json.dumps(cm),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        logger.info(f"ceph-csi-config updated in namespace {ns}")

    # Handle ceph-etc configmap in backups namespace separately
    if not check_configmap_exists("backups", "ceph-etc"):
        logger.info("Skipping backups (ceph-etc not found)")
        return
    logger.info("Updating ceph-etc in namespace backups")
    result = run_command("kubectl -n backups get cm ceph-etc -o json")
    cm = json.loads(result)

    config = json.loads(cm.get("data", {}).get("config.json", "[]"))
    changed = False
    for entry in config:
        current_monitors = entry.get("monitors", [])
        if sorted(current_monitors) != sorted(new_monitors):
            entry["monitors"] = new_monitors
            changed = True

    if not changed:
        logger.info("No monitor change detected in backups namespace, skipping update")
        return

    cm["data"]["config.json"] = json.dumps(config)

    subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=json.dumps(cm),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    logger.info("ceph-etc updated in namespace backups")

def main() -> None:
    """Update all Ceph ConfigMaps with current monitor information."""
    update_ceph_csi_configmaps()

if __name__ == "__main__":
    main()
