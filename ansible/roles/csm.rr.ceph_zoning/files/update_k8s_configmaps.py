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
This script updates Ceph monitor information in Kubernetes ConfigMaps
and the loftsman site-init secret after Ceph service zoning changes.
"""

import base64
import json
import logging
import subprocess
from typing import List
import yaml

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

def update_customizations() -> None:
    """
    Update the Ceph monitor addresses in the loftsman site-init secret
    (customizations.yaml) and the loftsman-cray-sysmgmt-health ConfigMap
    (cephExporter.endpoints).
    """
    # Both fields hold bare IPs, unlike the CSI monitors which include the :6789 port
    new_mons = [mon.rsplit(":", 1)[0] for mon in get_new_monitors()]

    logger.info("Extracting customizations.yaml from secret...")
    secret = json.loads(run_command("kubectl get secret -n loftsman site-init -o json"))
    customizations = yaml.safe_load(
        base64.b64decode(secret["data"]["customizations.yaml"]).decode("utf-8")
    )
    netstaticips = customizations.setdefault("spec", {}).setdefault("network", {}).setdefault(
        "netstaticips", {}
    )

    if sorted(netstaticips.get("nmn_ncn_storage_mons") or []) == sorted(new_mons):
        logger.info("nmn_ncn_storage_mons already up to date, skipping site-init update")
    else:
        logger.info("Updating monitor list in customizations.yaml...")
        netstaticips["nmn_ncn_storage_mons"] = new_mons
        secret["data"]["customizations.yaml"] = base64.b64encode(
            yaml.dump(customizations, default_flow_style=False).encode("utf-8")
        ).decode("ascii")

        # replace (not apply) avoids copying the whole secret into the last-applied annotation
        subprocess.run(
            ["kubectl", "replace", "-f", "-"],
            input=json.dumps(secret),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        logger.info("customizations secret updated successfully")

    logger.info("Updating cephExporter endpoints in loftsman-cray-sysmgmt-health...")

    if not check_configmap_exists("loftsman", "loftsman-cray-sysmgmt-health"):
        logger.info("Skipping loftsman-cray-sysmgmt-health (ConfigMap not found)")
        return

    result = run_command(
        "kubectl get cm -n loftsman loftsman-cray-sysmgmt-health "
        "-o jsonpath='{.data.manifest\\.yaml}'"
    )
    manifest_raw = result.strip().strip("'")
    if not manifest_raw:
        logger.info("Skipping loftsman-cray-sysmgmt-health (manifest.yaml is empty)")
        return

    manifest = yaml.safe_load(manifest_raw)
    if not isinstance(manifest, dict):
        logger.info("Skipping loftsman-cray-sysmgmt-health (manifest.yaml is not a mapping)")
        return

    charts = manifest.get("spec", {}).get("charts", [])
    if all(
        sorted(chart.get("values", {}).get("cephExporter", {}).get("endpoints") or []) == sorted(new_mons)
        for chart in charts
    ):
        logger.info("cephExporter endpoints already up to date, skipping loftsman-cray-sysmgmt-health update")
        return

    # Update cephExporter.endpoints in all charts
    for chart in charts:
        chart.setdefault("values", {}).setdefault("cephExporter", {})[
            "endpoints"
        ] = new_mons

    updated_manifest = yaml.dump(manifest, default_flow_style=False)

    patch_payload = json.dumps({"data": {"manifest.yaml": updated_manifest}})
    subprocess.run(
        [
            "kubectl", "patch", "cm", "-n", "loftsman",
            "loftsman-cray-sysmgmt-health",
            "--type", "merge",
            "-p", patch_payload,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    logger.info("loftsman-cray-sysmgmt-health ConfigMap updated successfully")


def main() -> None:
    """Update all Ceph ConfigMaps and customizations with current monitor information."""
    update_ceph_csi_configmaps()
    update_customizations()

if __name__ == "__main__":
    main()
