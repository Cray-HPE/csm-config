# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.15.28] - 2024-02-22

### Changed

- Append `?auth-basic` to SLES mirror zypper URLs to prevent artifactory from locking out the user during builds
- Use SLES package mirrors on `artifactory` instead of `slemaster`, to resolve build issues.

## [1.15.27] - 2024-02-21

- [CASMTRIAGE-6617](https://jira-pro.it.hpe.com:8443/browse/CASMTRIAGE-6617) Breakout Kernel Upgrade from ncn-initrd.yml AND dynamically install [NETETH-2313](https://jira-pro.it.hpe.com:8443/browse/NETETH-2313) for ALL products

## [1.15.26] - 2024-01-30

- [MTL-2348](https://jira-pro.it.hpe.com:8443/browse/MTL-2348): Ensure QLogic modules are included in initrd with the absence of `fastlinq.conf`, otherwise QLogic nodes will not boot.

## [1.15.25] - 2024-01-26

- [MTL-2348](https://jira-pro.it.hpe.com:8443/browse/MTL-2348): Use different Kubernetes secret

## [1.15.24] - 2024-01-24

- [MTL-2348](https://jira-pro.it.hpe.com:8443/browse/MTL-2348): New `ncn_kernel_upgrade` role. This role is now included in the `ncn_initrd.yml` playbook. These changes will
  enforce the installation of the new SuSE PTF Kernel and Marvell KMP. Module tweaks are also included, preventing `qedr`
  from loading during the rootfs, as well as being excluded from dracut.

## [1.15.23] - 2023-10-13

### Changed

- CASMINST-6690: update curl to address CVE-2023-38545

## [1.15.22] - 2023-09-22

### Changed

- MTL-2281: don't use FQCNs; older CSM ansible versions have bugs

## [1.15.21] - 2023-09-21

### Changed

- CASMINST-6624: Provide RPMs needed for enabling SMART data on UAN.

## [1.15.20] - 2023-09-14

### Changed

- MTL-2216: fixup mising env var

## [1.15.19] - 2023-09-14

### Changed

- MTL-2216: add role to apply CVE migitations

## [1.15.18] - 2023-08-16

### Changed

- CASMTRIAGE-5846: Change `sysctl_set` to be dynamic to prevent failure when building images
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds

## [1.15.17] - 2023-08-14

### Changed

= CASMCMS-8691: Update Docker file to account for changed RPM locations

## [1.15.16] - 2023-08-08

### Changed

- CASMTRIAGE-5788: Fixed `ncn_sysctl.yml` with the correct content from #163 and the fixes from #168

## [1.15.15] - 2023-08-08

### Removed

- CASMTRIAGE-5817: Removed `csm-node-identity` from NCN and Compute node package lists in `csm_packages`.

## [1.15.14] - 2023-08-03

### Added

- CASMTRIAGE-5788
  -  Use `sysctl` defaults removed by MTL-1974 to [`ansible/roles/csm.ncn.sysctl/vars/main.yml`](ansible/roles/csm.ncn.sysctl/vars/main.yml)
  - Invoke `csm.ncn.sysctl` in `ncn_nodes.yml` as well as all three playbooks invoked by `site.yml`

### Changed

- Replace all `ansible_os_family` and `ansible_distribution` conditionals for `SLE_HPC` with `ansible_distribution_file_variety == "SUSE"` to be
  agnostic to the SUSE product line (enabling usage on GCP images in `vshastav1` and `vshastav-future` once we move to hypervisors)

## [1.15.13] - 2023-07-05

### Changed

- CASMINST-6532: Add the following packages to the list that are installed/updated on NCNs in `csm_packages`:
  - `cfs-state-reporter`
  - `cfs-trust`
  - `craycli`
  - `csm-node-identity`
  - `csm-testing`
  - `goss-servers`
  - `hpe-csm-goss-package`
  - `hpe-csm-scripts`
  - `hpe-csm-yq-package`
  - `manifestgen`
- CASMINST-6532: Add the following packages to the list that are installed/updated on Compute nodes in `csm_packages`:
  - `csm-node-identity`

### Fixed

- CASMINST-6532: Ansible role `csm.packages`: Corrected default value for repository list to be an empty list, not an empty dictionary.

## [1.15.12] - 2023-03-29

### Changed

- CASMINST-6131: Allow CFS to set credentials in NCN images; remove duplicate call to set SSH keys on storage nodes

## [1.15.11] - 2023-03-28

### Changed

- CASMNET-2085: Allow `enable-chn.yml` to be a no-op during Image Customization

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

### Changed

- CASMINST-6051: added embedded CSM repo

## [1.15.7] - 2023-03-08

### Changed

- CASMCMS-8441: Use csm-helm-charts mirror in ct.yaml checks

## [1.15.6] - 2023-03-08

### Changed

- CASMCMS-8441: Use csm-rpms/csm-docker mirrors when building image; remove old commented lines from Dockerfile

## [1.15.5] - 2023-03-03
### Changed
- CASMINST-6041: allow ncn-initrd.yml to be used with all image types

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
- added a role and playbook for creating an NCN initrd

## [1.12.0] - 2022-08-16
### Changed
- make Dockerfile update base image with security patches

## [1.11.0] - 2022-08-01
### Added
- added conditional to csm.ncn.ca_cert checks for the existence of certificate_authority.crt before proceeding
- added csm.ncn.ca_cert role to install platform cert

### Removed
- Removed HMS test RPMs from CSM packages list, as they are no longer used as of CSM 1.3

## [1.10.1] - 2022-07-21

### Added

- Defined csm-sle-15sp3 zypper repository

### Changed

- Modified build to create valid unstable charts
- Added Mitch Harding as a maintainer
- Update minor version number used for csm-ssh-keys and cf-gitea-import

### Removed

- Removed leftover build files from old dynamic versioning system
- Removed Randy Kleinman as a maintainer

## [1.10.0] - 2022-07-05
### Changed

- Convert to gitflow/gitversion.

### Added

- Ansible playbook for applying csm packages to Compute and Application nodes

[Unreleased]: https://github.com/Cray-HPE/csm-config/compare/1.15.28...HEAD

[1.15.28]: https://github.com/Cray-HPE/csm-config/compare/1.15.27...1.15.28

[1.15.27]: https://github.com/Cray-HPE/csm-config/compare/1.15.26...1.15.27

[1.15.26]: https://github.com/Cray-HPE/csm-config/compare/1.15.25...1.15.26

[1.15.25]: https://github.com/Cray-HPE/csm-config/compare/1.15.24...1.15.25

[1.15.24]: https://github.com/Cray-HPE/csm-config/compare/1.15.23...1.15.24

[1.15.23]: https://github.com/Cray-HPE/csm-config/compare/1.15.22...1.15.23

[1.15.22]: https://github.com/Cray-HPE/csm-config/compare/1.15.21...1.15.22

[1.15.21]: https://github.com/Cray-HPE/csm-config/compare/1.15.20...1.15.21

[1.15.20]: https://github.com/Cray-HPE/csm-config/compare/1.15.19...1.15.20

[1.15.19]: https://github.com/Cray-HPE/csm-config/compare/1.15.18...1.15.19

[1.15.18]: https://github.com/Cray-HPE/csm-config/compare/1.15.17...1.15.18

[1.15.17]: https://github.com/Cray-HPE/csm-config/compare/1.15.16...1.15.17

[1.15.16]: https://github.com/Cray-HPE/csm-config/compare/1.15.15...1.15.16

[1.15.15]: https://github.com/Cray-HPE/csm-config/compare/1.15.14...1.15.15

[1.15.14]: https://github.com/Cray-HPE/csm-config/compare/1.15.13...1.15.14

[1.15.13]: https://github.com/Cray-HPE/csm-config/compare/1.15.12...1.15.13

[1.15.12]: https://github.com/Cray-HPE/csm-config/compare/1.15.11...1.15.12

[1.15.11]: https://github.com/Cray-HPE/csm-config/compare/1.15.10...1.15.11

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
