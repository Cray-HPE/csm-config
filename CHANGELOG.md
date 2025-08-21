# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.48.2] - 2025-08-20

### Changed

- CASMPET-7660: Changes to `sbps_dns_srv_records.sh` in `csm.sbps.dns_srv_records`
  - Fail if `SYSTEM_NAME` or `SITE_DOMAIN` are not set
  - Added echo statements role, to make it easier to debug in case of failure
  - Remove `-s` and `-f` flags from `curl` calls, and add `-i` flag, so they will
    give error messages and information on failure.

## [1.48.1] - 2025-08-19

### Fixed

- CASMTRIAGE-8638: RR k8s zone prefix is not getting applied correctly
  - Fixed `csm.rr.k8s_topology_zoning` role to use correct YAML path.

## [1.48.0] - 2025-08-15

### Fixed

- CASM-5685: RR storage play still assumes kubectl configured on all storage nodes
  - Fixed csm.rr.mgmt_nodes_placement_discovery role to use native Ansible (for kubectl) inside the
    CFS pod to get the information from Kubernetes instead of getting it from the node directly.
## [1.47.0] - 2025-08-14

### Changed

- CASM-5681:
  - Modify `csm.rr.check_enablement` role to set `ceph_prefix` fact from `customizations.yaml`,
    for use by other roles
  - Modify `csm.rr.ceph_zoning` to use the `ceph_prefix` fact
  - Modify `csm.rr.ceph_zoning` to run Ceph zoning and haproxy tasks only once. If already run, skip these roles. 

### Removed

- CASM-5676 (RR needlessly restarts deployments), 
  CASM-5677 (RR always overwrites Kyverno policy),
  CASM-5678 (RR restarts wrong deployments):
    - Remove `csm.rr.kyverno_policy` role from `csm-config`

### Dependencies

- Bump `actions/checkout` from 4 to 5 ([#402](https://github.com/Cray-HPE/csm-config/pull/402))

## [1.46.1] - 2025-08-12

### Fixed

- CASMCMS-9512: Modify the `csm.ssh_config` and `csm.ssh_keys` roles so that they no longer
  call `end_play` when they are only actually wanting to end the role.

## [1.46.0] - 2025-08-01

### Changed

- CASM-5672: Run placement validation in storage stanza, to prevent storage configuration when placement validation fails
- CASM-8567: Moved `csm.rr.ceph_zoning` Ansible role from management node flow to storage-specific section to better align with Ceph-specific operations.
- CASM-5671: Modify `csm.rr.check_enablement` role
  - Rather than assuming that RR is enabled unless it is explicitly set to disabled,
    instead assume that it is disabled unless it is explicitly set to enabled
  - Re-implement Python script in native Ansible
  - Modify so it runs inside the CFS pod
  - Save the result as an Ansible fact so that if both plays in the playbook run,
    this only needs to be done once.

### Fixed

- CASM-8567: Corrected typo in Kubernetes rollout restart command: `deploymet` → `deployment` for `cray-ceph-csi-cephfs-provisioner`.

## [1.45.0] - 2025-07-23

### Changed

- CASM-5661: RR Ansible play only checks for RR enablement sometimes
- CASM-5660: Changed to skip enabling/ configuring Rack Resiliency instead of failing 
  the configuration when it is disabled in the site-init (customizations.yaml) config.

## [1.44.0] - 2025-07-22

### Added

- CASM-5656
  - Added new role `csm.rr.ceph_haproxy` for CEPH haproxy config update
  - Tasks related to CEPH haproxy are moved from `csm.rr.ceph_zoning` to above new role
  - playbook `rack_resiliency_for_mgmt_nodes.yml` is update accordingly with above changes

### Fixed

- CASM-5656
  - Fixed typo in `ceph_haproxy.sh` of role `csm.rr.ceph_haproxy`

## [1.43.0] - 2025-07-17

### Added

- CASM-5626: Added new tasks for CEPH haproxy config update in `main.yml` for role `csm.rr.ceph_zoning`

### Changed

- CASM-5626
  - Changed the hosts for RR CEPH ansible play books in `rack_resiliency_for_mgmt_nodes.yml`
  - Updated logic in scripts `ceph_zoning.py` and `ceph_haproxy.sh`

## [1.42.1] - 2025-07-15

### Changed
- CASMPET-7624: Add check to beginning of `csm.sbps.apply_label`, to make sure that if the HSM iSCSI
  group exists, that it contains at least one worker NCN. If it does not, fail the playbook for all hosts
  with an appropriate error message.
- CASMPET-7625: Modified apply_label role to run only once, and inside the CFS pod, since nothing it does requires
  the target nodes to be up and running. This will allow node labels to be updated for every worker, whether or not they
  are up at the time the playbook is run.

## [1.42.0] - 2025-07-10

### Changed

- CASMPET-7616: Modify iSCSI playbook to be aware of new HSM group
  - The playbook runs on all worker nodes, and does the iSCSI configuration on all of them.
  - The `csm.sbps.apply_label` role behavior has changed. Now all workers in the group will have the
    label applied to them, and all workers not in the group will have the label removed from them.
  - The `csm.sbps.dns_srv_records` role previously queried SLS and made DNS entries for all worker
    nodes. Now it instead does this for all worker nodes that have the iSCSI Kubernetes label.
  - For the purposes of these changes, if the new HSM group does not exist, it is the same as if it
    exists and all workers belong to it.

## [1.41.0] - 2025-06-25

### Changed

- CASMTRIAGE-8171
  - Changed the order of iSCSI ansible play books execution in `config_sbps_iscsi_targets.yml`
  - Added target port disable functionality in `provision_iscsi_server.sh`

## [1.40.0] - 2025-06-23

### Added

- CASMMON-548: Add `cray-node-exporter` to the  package list. Revert CASMMON-534.

## [1.39.0] - 2025-06-17

### Changed

- MTL-2581: move uss specific packages into separate vars file to avoid installing them in csm compute images

## [1.38.0] - 2025-06-03

### Removed

- CASMMON-534: Remove `cray-node-exporter` from package list.

## [1.37.0] - 2025-05-28

### Removed

- CASMCMS-9447: Remove top-level playbooks that have been deprecated (in favor of `ncn_nodes.yml`) since CSM 1.4:
  - `ncn-master_nodes.yml`
  - `ncn-storage_nodes.yml`
  - `ncn-worker_nodes.yml`

## [1.36.0] - 2025-05-28

### Removed

- CASMCMS-9445: Remove `cray-uai-util` from package list (since UAI/UAS was removed in CSM 1.6)

## [1.35.0] - 2025-05-28

### Added

- CASMPET-7260
  - Added support for selective worker node personalization for iSCSI SBPS
  - This achieved by creating HSM groups before bootprep time
  - Added HSM group name `iscsi_worker` in `config_sbps_iscsi_targets.yml` in place of `Management_Worker`

## [1.34.0] - 2025-05-27

### Added

- CASMCMS-9439
  - Added `csm.ssh_config` roles to restore user SSH configuration from Vault
  - Added calls to this role to top-level NCN playbooks that called `csm.ssh_keys`
  - Created new top-level playbook `rotate-ssh-config-mgmt-nodes.yml`, akin to `rotate-ssh-keys-mgmt-nodes.yml`

### Changed

- MTL-2569/MTL-2574/MTL-2556/MTL-2555/MTL-2573: RPMs transferred from COS to CSM
  - csm-sbps-dracut
  - csm-sbps-utils
  - csm-udev-network (cn and ncn)
  - csm-netif-dracut
  - csm-scripts-dracut

## [1.33.0] - 2025-05-12

### Added

- CASM-4872: Rack Resiliency (RR): Provide a method for placement discovery and validation of management nodes in order to meet the RR norms
- CASM-4873: Rack Resiliency (RR): Define, create, and configure Management Plane Failure Domains and handle enablement/disablement of the RR feature

RR Ansible plays for:
  - handling enablement/disablement of the RR feature
  - discovery of physical racks and management nodes (master, worker, and storage)
  - management nodes placement validation
  - k8s topology zoning for master and worker nodes
  - CEPH zoning for storage nodes
  - RR kyverno policy for equal distribution of critical services

## [1.32.0] - 2025-04-16

### Fixed

- CASMPET-7443: correctly detect curl failures in `sbps_dns_srv_records.sh`
- CASMPET-7444: handle CRLFs in script output in `sbps_dns_srv_records.sh`

### Changed

- CASMTRIAGE-8069: Add `net.ipv4.neigh.default.base_reachable_time_ms` to `roles/csm.ncn.sysctl/vars/main.yml`

### Dependencies

- Bump `dangoslen/dependabot-changelog-helper` from 3 to 4 ([#340](https://github.com/Cray-HPE/csm-config/pull/340))

## [1.31.0] - 2025-02-18

### Dependencies

- CASMCMS-9282: Update to `csm-ssh-keys` to v1.7.0 for CSM 1.7
- CASMCMS-9282: Update to `cf-gitea-import` to v1.11.0 for CSM 1.7

## [1.30.0] - 2025-01-30

### Changed

- CASMCMS-9262: Update RPM lists in `vars/csm_packages.yml`

## [1.29.0] - 2025-01-24

### Changed

- CASMCMS-9258: Only install `cfs-debugger` RPM on management NCNs.

## [1.28.0] - 2024-12-10

### Fixed

- CASMTRIAGE-7469 - fixed problems with ansible plays to build IMS remote build node image.

## [1.27.4] - 2024-11-08

### Fixed

- CASMTRIAGE-7459: Enable iscsid.service in compute/UAN nodes

## [1.27.3] - 2024-11-05

### Fixed

- CASMTRIAGE-7445: Avoid re configuration of LIO targets when they are already configured for any worker node.

## [1.27.2] - 2024-10-29

### Fixed

- CASMTRIAGE-7447: CMN iSCSI portal can be used off system without authentication
  - Remove CMN iSCSI portal creation from the LIO provisioning as we
    are not using it for any projection unlike with HSN and NMN.

## [1.27.1] - 2024-10-28

### Fixed

- CASMTRIAGE-7428: iSCSI SBPS: Fixed DNS SRV A records creation part of node personalization at
  bootprep (management rollout).

## [1.27.0] - 2024-10-11

### Changed

- CASMPET-7254: Update the config_sbps_iscsi_targets.yml playbook so that it only runs during node
  personalization and not during image customization.

## [1.26.2] - 2024-10-09

### Fixed

- CASMTRIAGE-7373
  - Updated Spire hard link for iSCSI SBPS
  - Require `sbps-marshal` to be at least version `0.0.8`, the first version with the corrected hard link

## [1.26.1] - 2024-10-01

### Fixed

- CASMTRIAGE-7301: Ansible play to create iscsi-sbps-targets should not delegate to localhost
  - fixed the tasks, update file (with host, HSN and NMN info) and creation of DNS SRV and A records
    to delegate to one of the worker node instead of localhost.

## [1.26.0] - 2024-09-12

### Fixed

- CASMPET-7225: Fallback to default s3fs mount of boot-images bucket with IMS user policy
  - We must have writable access to "/var/lib/cps-local/boot-images" mount dir of "boot-images"
    bucket in order for CPS to function and also for user to have write access for removing 
    cos-config-data under this mount path, when he want to disable CPS.

    We need to keep this fallback option till CPS is removed in USS-1.3.

## [1.25.0] - 2024-09-12

### Added 

- MTL-1980: Configure a bonded HSN connection on an NCN

## [1.24.2] - 2024-08-23

### Added 

- CASMPET-7180: New CFS play to enable spire for SBPS Marshal Agent
- CASMPET-7195: New CFS play to install (+ previous enable) SBPS Marshal Agent

### Fixed
- typo fix in DNS SRV A records

## [1.24.1] - 2024-08-12

### Fixed

- CASMPET-7175: iSCSI SBPS: radosgw-admin cmd fails with "auth: unable to find a keyring..."
  part of s3fs mount for boot images (boot-images bucket)
      - fixed CFS play to create s3 access/ secret key on master node followed by mounting
        s3 boot images with this s3 key on worker nodes.

## [1.24.0] - 2024-08-09

### Fixed

- CASMPET-7117: iSCSI SBPS: LIO provision and DNS records config fails when HSN is not configured
  - fixed iSCSI LIO provisioning to exclude HSN portal config when HSN n/w is not configured
  - fixed to avoid DNS "SRV" and "A" records creation for HSN when HSN is not configured

- CASMPET-7126: iSCSI SBPS: k8s labelling fails when it is already applied
  - fixed to avoid applying k8s label when it is already exist

## [1.23.0] - 2024-08-08

### Dependencies

- CASMCMS-9082: Build Docker image on SLE15 SP6 (up from SP4)

## [1.22.0] - 2024-06-25

### Added

- CASMINST-6896: Add support for multiple GPG keys and update with CFS

## [1.21.0] - 2024-06-12

### Added

- CASMPET-6797(EPIC): Added Ansible plays to provision LIO services on iSCSI targets (worker NCNs) for SBPS
  - CASMPET-6887: Add Ansible play to configure LIO targets
  - CASMPET-6888: Add Ansible play to add/ update DNS `SRV` and `A` records for HSN and NMN using play script against PowerDNS API
  - CASMPET-6890
    - Add Ansible play to mount S3 bucket `boot-images` using `s3fs` read-only policy for SBPS
    - Start SBPS Marshal agent systemd service (post-install) during node personalization
      on the selected worker nodes.
  - CASMPET-6933: Add Ansible play to apply k8s labels for SBPS on specified number of worker NCNs

## [1.20.0] - 2024-05-30

### Added

- ansible role for creating pdsh group files based on data from sls

## [1.19.0] - 2024-05-21

### Added

- 'statedir' environment variable to support a newer version of the ca-certificates rpm

## [1.18.0] - 2024-03-20

### Added

- SKERN-9239: Added password-less ssh to CN/UAN to CSM layer

### Removed

- CASMTRIAGE-6787: `net.ipv4.conf.all.rp_filter` tunable no longer set in `ansible/roles/csm.ncn.sysctl/vars/main.yml`

## [1.17.11] - 2024-03-04

### Added

- Added support for `aarch64` IMS remote nodes

## [1.17.10] - 2024-02-28

### Fixed

- Fixed typo in `ansible/ims_computes.yml`

## [1.17.9] - 2024-02-23

### Changed

- Added DNS workaround for GCP

## [1.17.8] - 2024-02-22

### Changed

- Append `?auth-basic` to SLES mirror zypper URLs to prevent artifactory from locking out the user during builds

## [1.17.7] - 2024-02-22

### Changed

- Use SLES package mirrors on `artifactory` instead of `slemaster`, to resolve build issues.

## [1.17.6] - 2024-02-22

### Dependencies

- Bump `csm-ssh-keys` from 1.5 to 1.6 for CSM 1.6

## [1.17.5] - 2024-02-01

### Added

- CASMTRIAGE-6582: add new links for services to use the proper spire-agent version.

## [1.17.4] - 2024-01-05

### Added

- CASMPET-6814: `vars/csm_packages.yml`: Add `cray-spire-dracut>=2.0.0`, `spire-agent>=1.5.0`, and `tpm-provisioner` to allow for a TPM-enabled Spire.

## [1.17.3] - 2024-01-05

### Dependencies

- Bump `cf-gitea-import` from `1.9` to `1.10`

## [1.17.2] - 2023-12-05

### Changed

- CASMTRIAGE-6370: Change the `csm.storage.smartmon` play so it redeploys `node-exporter` using a specific image with the cephadm shell.

## [1.17.1] - 2023-11-20

### Changed

- CASMPET-6860: Change the `csm.storage.smartmon` play so it redeploys `node-exporter` using 'cephadm shell' instead of a 'ceph' command.

## [1.17.0] - 2023-10-18

### Dependencies

- Bump `stefanzweifel/git-auto-commit-action` from 4 to 5 ([#212](https://github.com/Cray-HPE/csm-config/pull/212))

### Added

- CRAYSAT-1767: Added the role `csm.ncn.sat` for configuration of the System
  Admin Toolkit (SAT). A similar role for SAT configuraiton was previously only
  provided by the SAT product.

## [1.16.22] - 2023-09-26

### Changed

- CASMINST-6666: Change the `csm.storage.smartmon` play so it only redeploys `node-exporter` if the ceph admin keyring exists.

## [1.16.21] - 2023-09-22

### Changed

- CASMCMS-8696: Create an Ansible play that configures a compute image for IMS builds.

## [1.16.20] - 2023-09-21

### Added

- CASMINST-6667: Include `cray-uai-util` package in compute nodes
- CASMINST-6662: Enable `csm-node-heartbeat` and `csm-node-identity` services on compute and
  application nodes in `csm_packages.yml`.

### Changed

- CASMINST-6662: Ensure that `systemd` preset changes are applied after preset file is updated
  in `csm_packages.yml`.

## [1.16.19] - 2023-09-12

### Changed

- CASMINST-6624: Provide RPMs needed for enabling SMART data on UAN

### Dependencies

- Bump `actions/checkout` from 3 to 4 ([#187](https://github.com/Cray-HPE/csm-config/pull/187))

## [1.16.18] - 2023-08-24

### Changed

- CASMMON-337: Smartmon role should not run during image customization, only on live storage NCNs.

## [1.16.17] - 2023-08-16

### Changed

- CASMTRIAGE-5846: Change `sysctl_set` to be dynamic to prevent failure when building images
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds

## [1.16.16] - 2023-08-14

### Changed

= CASMCMS-8691: Update Docker file to account for changed RPM locations

### Changed

## [1.16.15] - 2023-08-09

### Changed

- CASMCMS-8758: Add more RPMs to CSM packages lists; split out Application and Compute node package lists

## [1.16.14] - 2023-08-08

### Changed

- CASMTRIAGE-5788: Prevents YAML interpolation of `hosts: &cfs_image` in `ncn_sysctl.yml`, allowing the playbook to run.

## [1.16.13] - 2023-08-03

### Changed

- CASMTRIAGE-5788
    - Invoke `csm.ncn.sysctl` in `ncn_nodes.yml`, and all three playbooks invoked by `site.yml`
    - Rename `ncn-sysctl.yml` to `ncn_sysctl.yml` to follow the implicit naming convention in the repo
- Replace all `ansible_os_family` and `ansible_distribution` conditionals for `SLE_HPC` with `ansible_distribution_file_variety == "SUSE"` to be
  agnostic to the SUSE product line (enabling usage on GCP images in `vshastav1` and `vshastav-future` once we move to hypervisors)

## [1.16.12] - 2023-08-03

### Added

- CASMTRIAGE-5788
  -  Use `sysctl` defaults removed by MTL-1974 to [`ansible/roles/csm.ncn.sysctl/vars/main.yml`](ansible/roles/csm.ncn.sysctl/vars/main.yml)

## [1.16.11] - 2023-08-01

### Added

- CASMTRIAGE-5793
  -  Fix `node-exporter` filename extension in [`ansible/roles/csm.storage.smartmon/tasks/main.yml`](ansible/roles/csm.storage.smartmon/tasks/main.yml)

## [1.16.10] - 2023-07-28

### Added

- CASMMON-333
  -  New package `storage_mgmt_ncn_csm_sles_packages` for including new `smart-mon` RPM.
  -  New role `csm.storage.smartmon` to start the SMART service; reconfigure and redeploy `node-exporter`.

### Changed

- Modified `compute_nodes.yml` top-level play to actually include compute nodes (instead of just application nodes)

## [1.16.9] - 2023-07-20

### Changed

- MTL-2000/CASMINST-3431: Modify [`csm_repos.yml`](ansible/vars/csm_repos.yml) so that instead of adding Zypper repos for
  every SLE version, it only adds the Zypper repository for the SLE version where the play is being run; the `csm-noos`
  repo is always still added.

## [1.16.8] - 2023-07-06

### Changed

- CASMINST-6535
  - Reorganize the plays in [`ncn_nodes.yml`](ansible/ncn_nodes.yml) to take advantage of Ansible package install optimizations.
  - [`csm_packages.yml`](ansible/vars/csm_packages.yml): Rename `ncn_csm_sles_packages` to `common_mgmt_ncn_csm_sles_packages`
  - [`csm_packages.yml`](ansible/vars/csm_packages.yml): Rename `k8s_ncn_csm_sles_packages` to `k8s_mgmt_ncn_csm_sles_packages`

## [1.16.7] - 2023-07-05

### Changed

- CASMINST-6532: Split the `csm_packages` lists into `common_csm_sles_packages` (installed on all SLES nodes),
  `ncn_csm_sles_packages` (installed on all management NCNs), `k8s_ncn_csm_sles_packages` (installed on all
  master/worker NCNs), and `compute_csm_sles_packages` (installed on all SLES application and compute nodes).
  Modified the plays accordingly.
- CASMINST-6532: Added some RPMs that were missing from the NCN list:
  - `cfs-state-reporter`
  - `cfs-trust`
  - `craycli`
  - `csm-auth-utils`
  - `csm-node-heartbeat`
  - `csm-node-identity`
  - `csm-testing`
  - `goss-servers`
  - `hpe-csm-goss-package`
  - `hpe-csm-scripts`
  - `hpe-yq`
  - `manifestgen`
  - `spire-agent`
- CASMINST-6532: Moved `cmstools` to the `k8s_ncn_csm_sles_packages` list so that it would not be installed on
  storage NCNs, where it does not work.

### Fixed

- CASMINST-6532: Ansible role `csm.packages`: Corrected default value for repository list to be an empty list, not an empty dictionary.

## [1.16.6] - 2023-06-28

### Added

- CASMCMS-8537: Documentation and sample role for IMS passthrough variables

## [1.16.5] - 2023-06-26

### Added

- CASM-4085: Add sysctl role for modifying kernel parameters

## [1.16.4] - 2023-06-22

### Added

- MTL-2018: Include `acpid`
- MTL-2019: Include `csm-node-heartbeat`

## [1.16.3] - 2023-06-02

### Added

- MTL-2016: Include `csm-auth-utils` in `csm-packages`
- CASMINST-3421: Include the new `noos` repository in `csm-repos`

## [1.16.2] - 2023-03-29

### Changed

- CASMINST-6131: Allow CFS to set credentials in NCN images; remove duplicate call to set SSH keys on storage nodes

## [1.16.1] - 2023-03-28

### Changed

- CASMNET-2085: Allow `enable-chn.yml` to be a no-op during Image Customization

## [1.16.0] - 2023-03-23

### Added

- MTL-2014: Include `spire-agent` in `csm-packages`
- MTL-2025: Include `csm-node-identity` in `csm-packages`
- CASM-3071/MTL-2021: Add ansible code for the csm-compute image

## [1.15.10] - 2023-03-17

### Changed

- CASMCMS-8470: Use artifactory authentication instead of building from unauthenticated artifactory mirrors

## [1.15.9] - 2023-03-14

### Changed

- CASMTRIAGE-5050: Enable targeted fact-gathering in [`csm_packages.yml`](ansible/csm_packages.yml) to ensure that the `ansible_distribution` variable is set
- CASMCMS-8461: Use cf-gitea-import version 1.9

### Removed

- CASMCMS-8461: Removed vestigial file leftover from former dynamic versioning system.

## [1.15.8] - 2023-03-08

### Added

- CASMINST-6051: added embedded CSM repo

## [1.15.7] - 2023-03-08

### Changed

- CASMCMS-8441: Use csm-helm-charts mirror in ct.yaml checks

## [1.15.6] - 2023-03-08

### Changed

- CASMCMS-8441: Use csm-rpms/csm-docker mirrors when building image; remove old commented lines from Dockerfile

## [1.15.5] - 2023-03-03

### Changed

- CASMINST-6041: allow `ncn-initrd.yml` to be used with all image types

## [1.15.4] - 2023-03-01

### Changed

- CASMTRIAGE-5003: Package installation for Compute nodes will only run during image customization

## [1.15.3] - 2023-02-10

### Added

- CONTRIBUTING.md file
- CASMCMS-8241: Added unified csm management node playbook ncn_nodes.yml
- CASMCMS-5516: Added cfs-debugger to ncn packages
- Two packages craycli and cray-uai-util to compute and application playbook

### Changed

- CASMCMS-8242: Converted ncn-initrd.yml over to new cfs_image host protocol invocation
- CASMCMS-8241: Broke ncn-(master,storage,worker)_nodes.yml into node and node+image specific playbooks
- CASMCMS-8240: Allow packages to be installed during image customization

## [1.15.2] - 2023-02-10

### Added

- Two packages craycli and cray-uai-util to compute and application playbook

## [1.15.1] - 2022-12-20

### Added

- Add Artifactory authentication to Jenkinsfile

## [1.15.0] - 2022-09-12

### Changed

- CASMCMS-8076: Changed base image to use sp4

## [1.14.0] - 2022-09-08

### Added

- Defined csm-sle-15sp4 zypper repository

## [1.13.0] - 2022-09-02

### Added

- Added a role and playbook for creating an NCN initrd

## [1.12.0] - 2022-08-16

### Changed

- Make Dockerfile update base image with security patches

## [1.11.0] - 2022-08-01

### Changed

- Added conditional to csm.ca_cert checks for the existence of certificate_authority.crt before proceeding

### Added

- Added csm.ca_cert role to install platform cert

### Removed

- Removed HMS test RPMs from CSM packages list, as they are no longer used as of CSM 1.3

## [1.10.1] - 2022-07-21

### Added

- Defined csm-sle-15sp3 zypper repository
- Added Mitch Harding as a maintainer

### Changed

- Modified build to create valid unstable charts
- Update minor version number used for csm-ssh-keys and cf-gitea-import

### Removed

- Removed leftover build files from old dynamic versioning system
- Removed Randy Kleinman as a maintainer

## [1.10.0] - 2022-07-05

### Changed

- Convert to gitflow/gitversion.

### Added

- Ansible playbook for applying csm packages to Compute and Application nodes

[Unreleased]: https://github.com/Cray-HPE/csm-config/compare/1.48.2...HEAD

[1.48.2]: https://github.com/Cray-HPE/csm-config/compare/1.48.1...1.48.2

[1.48.1]: https://github.com/Cray-HPE/csm-config/compare/1.48.0...1.48.1

[1.48.0]: https://github.com/Cray-HPE/csm-config/compare/1.47.0...1.48.0

[1.47.0]: https://github.com/Cray-HPE/csm-config/compare/1.46.1...1.47.0

[1.46.1]: https://github.com/Cray-HPE/csm-config/compare/1.46.0...1.46.1

[1.46.0]: https://github.com/Cray-HPE/csm-config/compare/1.45.0...1.46.0

[1.45.0]: https://github.com/Cray-HPE/csm-config/compare/1.44.0...1.45.0

[1.44.0]: https://github.com/Cray-HPE/csm-config/compare/1.43.0...1.44.0

[1.43.0]: https://github.com/Cray-HPE/csm-config/compare/1.42.1...1.43.0

[1.42.1]: https://github.com/Cray-HPE/csm-config/compare/1.42.0...1.42.1

[1.42.0]: https://github.com/Cray-HPE/csm-config/compare/1.41.0...1.42.0

[1.41.0]: https://github.com/Cray-HPE/csm-config/compare/1.40.0...1.41.0

[1.40.0]: https://github.com/Cray-HPE/csm-config/compare/1.39.0...1.40.0

[1.39.0]: https://github.com/Cray-HPE/csm-config/compare/1.38.0...1.39.0

[1.38.0]: https://github.com/Cray-HPE/csm-config/compare/1.37.0...1.38.0

[1.37.0]: https://github.com/Cray-HPE/csm-config/compare/1.36.0...1.37.0

[1.36.0]: https://github.com/Cray-HPE/csm-config/compare/1.35.0...1.36.0

[1.35.0]: https://github.com/Cray-HPE/csm-config/compare/1.34.0...1.35.0

[1.34.0]: https://github.com/Cray-HPE/csm-config/compare/1.33.0...1.34.0

[1.33.0]: https://github.com/Cray-HPE/csm-config/compare/1.32.0...1.33.0

[1.32.0]: https://github.com/Cray-HPE/csm-config/compare/1.31.0...1.32.0

[1.31.0]: https://github.com/Cray-HPE/csm-config/compare/1.30.0...1.31.0

[1.30.0]: https://github.com/Cray-HPE/csm-config/compare/1.29.0...1.30.0

[1.29.0]: https://github.com/Cray-HPE/csm-config/compare/1.28.0...1.29.0

[1.28.0]: https://github.com/Cray-HPE/csm-config/compare/1.27.4...1.28.0

[1.27.4]: https://github.com/Cray-HPE/csm-config/compare/1.27.3...1.27.4

[1.27.3]: https://github.com/Cray-HPE/csm-config/compare/1.27.2...1.27.3

[1.27.2]: https://github.com/Cray-HPE/csm-config/compare/1.27.1...1.27.2

[1.27.1]: https://github.com/Cray-HPE/csm-config/compare/1.27.0...1.27.1

[1.27.0]: https://github.com/Cray-HPE/csm-config/compare/1.26.2...1.27.0

[1.26.2]: https://github.com/Cray-HPE/csm-config/compare/1.26.1...1.26.2

[1.26.1]: https://github.com/Cray-HPE/csm-config/compare/1.26.0...1.26.1

[1.26.0]: https://github.com/Cray-HPE/csm-config/compare/1.25.0...1.26.0

[1.25.0]: https://github.com/Cray-HPE/csm-config/compare/1.24.2...1.25.0

[1.24.2]: https://github.com/Cray-HPE/csm-config/compare/1.24.1...1.24.2

[1.24.1]: https://github.com/Cray-HPE/csm-config/compare/1.24.0...1.24.1

[1.24.0]: https://github.com/Cray-HPE/csm-config/compare/1.23.0...1.24.0

[1.23.0]: https://github.com/Cray-HPE/csm-config/compare/1.22.0...1.23.0

[1.22.0]: https://github.com/Cray-HPE/csm-config/compare/1.21.0...1.22.0

[1.21.0]: https://github.com/Cray-HPE/csm-config/compare/1.20.0...1.21.0

[1.20.0]: https://github.com/Cray-HPE/csm-config/compare/1.19.0...1.20.0

[1.19.0]: https://github.com/Cray-HPE/csm-config/compare/1.18.0...1.19.0

[1.18.0]: https://github.com/Cray-HPE/csm-config/compare/1.17.11...1.18.0

[1.17.11]: https://github.com/Cray-HPE/csm-config/compare/1.17.10...1.17.11

[1.17.10]: https://github.com/Cray-HPE/csm-config/compare/1.17.9...1.17.10

[1.17.9]: https://github.com/Cray-HPE/csm-config/compare/1.17.8...1.17.9

[1.17.8]: https://github.com/Cray-HPE/csm-config/compare/1.17.7...1.17.8

[1.17.7]: https://github.com/Cray-HPE/csm-config/compare/1.17.6...1.17.7

[1.17.6]: https://github.com/Cray-HPE/csm-config/compare/1.17.5...1.17.6

[1.17.5]: https://github.com/Cray-HPE/csm-config/compare/1.17.4...1.17.5

[1.17.4]: https://github.com/Cray-HPE/csm-config/compare/1.17.3...1.17.4

[1.17.3]: https://github.com/Cray-HPE/csm-config/compare/1.17.2...1.17.3

[1.17.2]: https://github.com/Cray-HPE/csm-config/compare/1.17.1...1.17.2

[1.17.1]: https://github.com/Cray-HPE/csm-config/compare/1.17.0...1.17.1

[1.17.0]: https://github.com/Cray-HPE/csm-config/compare/1.16.22...1.17.0

[1.16.22]: https://github.com/Cray-HPE/csm-config/compare/1.16.21...1.16.22

[1.16.21]: https://github.com/Cray-HPE/csm-config/compare/1.16.20...1.16.21

[1.16.20]: https://github.com/Cray-HPE/csm-config/compare/1.16.19...1.16.20

[1.16.19]: https://github.com/Cray-HPE/csm-config/compare/1.16.18...1.16.19

[1.16.18]: https://github.com/Cray-HPE/csm-config/compare/1.16.17...1.16.18

[1.16.17]: https://github.com/Cray-HPE/csm-config/compare/1.16.16...1.16.17

[1.16.16]: https://github.com/Cray-HPE/csm-config/compare/1.16.15...1.16.16

[1.16.15]: https://github.com/Cray-HPE/csm-config/compare/1.16.14...1.16.15

[1.16.14]: https://github.com/Cray-HPE/csm-config/compare/1.16.13...1.16.14

[1.16.13]: https://github.com/Cray-HPE/csm-config/compare/1.16.12...1.16.13

[1.16.12]: https://github.com/Cray-HPE/csm-config/compare/1.16.11...1.16.12

[1.16.11]: https://github.com/Cray-HPE/csm-config/compare/1.16.10...1.16.11

[1.16.10]: https://github.com/Cray-HPE/csm-config/compare/1.16.9...1.16.10

[1.16.9]: https://github.com/Cray-HPE/csm-config/compare/1.16.8...1.16.9

[1.16.8]: https://github.com/Cray-HPE/csm-config/compare/1.16.7...1.16.8

[1.16.7]: https://github.com/Cray-HPE/csm-config/compare/1.16.6...1.16.7

[1.16.6]: https://github.com/Cray-HPE/csm-config/compare/1.16.5...1.16.6

[1.16.5]: https://github.com/Cray-HPE/csm-config/compare/1.16.4...1.16.5

[1.16.4]: https://github.com/Cray-HPE/csm-config/compare/1.16.3...1.16.4

[1.16.3]: https://github.com/Cray-HPE/csm-config/compare/1.16.2...1.16.3

[1.16.2]: https://github.com/Cray-HPE/csm-config/compare/1.16.1...1.16.2

[1.16.1]: https://github.com/Cray-HPE/csm-config/compare/1.16.0...1.16.1

[1.16.0]: https://github.com/Cray-HPE/csm-config/compare/1.15.10...1.16.0

[1.15.10]: https://github.com/Cray-HPE/csm-config/compare/1.15.9...1.15.10

[1.15.9]: https://github.com/Cray-HPE/csm-config/compare/1.15.8...1.15.9

[1.15.8]: https://github.com/Cray-HPE/csm-config/compare/1.15.7...1.15.8

[1.15.7]: https://github.com/Cray-HPE/csm-config/compare/1.15.6...1.15.7

[1.15.6]: https://github.com/Cray-HPE/csm-config/compare/1.15.5...1.15.6

[1.15.5]: https://github.com/Cray-HPE/csm-config/compare/1.15.4...1.15.5

[1.15.4]: https://github.com/Cray-HPE/csm-config/compare/1.15.3...1.15.4

[1.15.3]: https://github.com/Cray-HPE/csm-config/compare/1.15.2...1.15.3

[1.15.2]: https://github.com/Cray-HPE/csm-config/compare/1.15.1...1.15.2

[1.15.1]: https://github.com/Cray-HPE/csm-config/compare/1.15.0...1.15.1

[1.15.0]: https://github.com/Cray-HPE/csm-config/compare/1.14.0...1.15.0

[1.14.0]: https://github.com/Cray-HPE/csm-config/compare/1.13.0...1.14.0

[1.13.0]: https://github.com/Cray-HPE/csm-config/compare/1.12.0...1.13.0

[1.12.0]: https://github.com/Cray-HPE/csm-config/compare/1.11.0...1.12.0

[1.11.0]: https://github.com/Cray-HPE/csm-config/compare/1.10.1...1.11.0

[1.10.1]: https://github.com/Cray-HPE/csm-config/compare/1.10.0...1.10.1

[1.10.0]: https://github.com/Cray-HPE/csm-config/compare/1.9.0...1.10.0
