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
import os
import shutil
import subprocess
import tempfile

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


def get_new_monitors() -> list[str]:
    """Get the current list of Ceph monitor addresses from the monitor map."""
    result = run_command("ceph mon dump -f json")
    mon_dump = json.loads(result)
    return [mon["public_addr"].split("/")[0] for mon in mon_dump["mons"]]


def update_ceph_csi_configmaps() -> None:
    """
    Update the monitors list in all Ceph CSI ConfigMaps across relevant
    namespaces using the current Ceph monitor map.
    """
    new_monitors = get_new_monitors()
    logger.info(f"New monitor list: {new_monitors}")

    # Namespaces ceph-rbd, ceph-cephfs, default, services contain ceph-csi-config configmap
    for ns in ["ceph-rbd", "ceph-cephfs", "default", "services"]:
        try:
            run_command(f"kubectl -n {ns} get cm ceph-csi-config")
        except Exception as e:
            logger.info(f"Skipping {ns} (ceph-csi-config not found): {e}")
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
            capture_output=True,
            text=True,
        )
        logger.info(f"ceph-csi-config updated in namespace {ns}")

    # Handle ceph-etc configmap in backups namespace separately
    try:
        run_command("kubectl -n backups get cm ceph-etc")
    except Exception as e:
        logger.info(f"Skipping backups (ceph-etc not found): {e}")
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
        capture_output=True,
        text=True,
    )
    logger.info("ceph-etc updated in namespace backups")


def update_customizations() -> None:
    """
    Update the Ceph monitor addresses in the loftsman site-init secret
    (customizations.yaml) and the loftsman-cray-sysmgmt-health ConfigMap
    (cephExporter.endpoints).
    """
    new_mons = get_new_monitors()
    tmpdir = tempfile.mkdtemp(dir=os.path.expanduser("~"))

    try:
        logger.info("Extracting customizations.yaml from secret...")

        result = run_command(
            "kubectl get secret -n loftsman site-init -o jsonpath='{.data.customizations\\.yaml}'"
        )
        customizations_b64 = result.strip().strip("'")
        customizations_raw = base64.b64decode(customizations_b64).decode("utf-8")

        customizations_path = os.path.join(tmpdir, "customizations.yaml")
        with open(customizations_path, "w") as f:
            f.write(customizations_raw)

        logger.info("Updating monitor list in customizations.yaml...")

        with open(customizations_path, "r") as f:
            customizations = yaml.safe_load(f)

        # Update nmn_ncn_storage_mons
        customizations.setdefault("spec", {}).setdefault("network", {}).setdefault(
            "netstaticips", {}
        )["nmn_ncn_storage_mons"] = new_mons

        with open(customizations_path, "w") as f:
            yaml.dump(customizations, f, default_flow_style=False)

        logger.info("Recreating site-init secret...")

        run_command("kubectl delete secret -n loftsman site-init --ignore-not-found")
        run_command(
            f"kubectl create secret -n loftsman generic site-init "
            f"--from-file={customizations_path}"
        )

        logger.info("customizations secret updated successfully")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    logger.info("Updating cephExporter endpoints in loftsman-cray-sysmgmt-health...")

    result = run_command(
        "kubectl get cm -n loftsman loftsman-cray-sysmgmt-health "
        "-o jsonpath='{.data.manifest\\.yaml}'"
    )
    manifest_raw = result.strip().strip("'")
    manifest = yaml.safe_load(manifest_raw)

    # Update cephExporter.endpoints in all charts
    for chart in manifest.get("spec", {}).get("charts", []):
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
        capture_output=True,
        text=True,
    )

    logger.info("loftsman-cray-sysmgmt-health ConfigMap updated successfully")


def main() -> None:
    """Update all Ceph ConfigMaps and customizations with current monitor information."""
    update_ceph_csi_configmaps()
    update_customizations()


if __name__ == "__main__":
    main()
