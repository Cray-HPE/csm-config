# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/Cray-HPE/csm-config/compare/1.14.0...HEAD

[1.14.0]: https://github.com/Cray-HPE/csm-config/compare/1.13.0...1.14.0

[1.13.0]: https://github.com/Cray-HPE/csm-config/compare/1.12.0...1.13.0

[1.12.0]: https://github.com/Cray-HPE/csm-config/compare/1.11.0...1.12.0

[1.11.0]: https://github.com/Cray-HPE/csm-config/compare/1.10.1...1.11.0

[1.10.1]: https://github.com/Cray-HPE/csm-config/compare/1.10.0...1.10.1

[1.10.0]: https://github.com/Cray-HPE/csm-config/compare/1.9.0...1.10.0
