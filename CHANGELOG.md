# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Cray-HPE/csm-config/compare/1.17.5...HEAD

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
