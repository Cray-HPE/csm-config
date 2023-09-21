# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

## [1.14.8] - 2023-10-06

### Added

- CASMINST-6662: Enable `cray-heartbeat` and `csm-node-identity` services on compute and
  application nodes in `csm_packages.yml`.

### Changed

- CASMINST-6662: Ensure that `systemd` preset changes are applied after preset file is updated
  in `csm_packages.yml`.

## [1.14.7] - 2023-09-22
### Reverted
- CASMINST-6624: Provide RPMs needed for enabling SMART data on UAN

## [1.14.6] - 2023-09-22
### Changed
- MTL-2281: don't use FQCNs; older CSM ansible versions have bugs

## [1.14.5] - 2023-09-14
### Changed
- MTL-2216: fixup mising env var definition

## [1.14.4] - 2023-09-14
### Changed
- MTL-2216: add role to apply CVE migitations

## [1.14.3] - 2023-09-08
### Changed
- CASMINST-6624: Provide RPMs needed for enabling SMART data on UAN
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds
- CASMCMS-8691: Update Docker file to account for changed RPM locations
- CASMCMS-8470: Use artifactory authentication instead of building from unauthenticated artifactory mirrors
- CASMCMS-8441: Use csm-rpms/csm-docker mirrors when building image; remove old commented lines from Dockerfile

## [1.14.2] - 2023-03-01
### Changed
- CASMTRIAGE-5003: Package installation for Compute nodes will only run during image customization

## [1.14.1] - 2023-01-06
### Added
- Add Artifactory authentication to Jenkinsfile

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

[Unreleased]: https://github.com/Cray-HPE/csm-config/compare/1.14.8...HEAD

[1.14.8]: https://github.com/Cray-HPE/csm-config/compare/1.14.7...1.14.8

[1.14.7]: https://github.com/Cray-HPE/csm-config/compare/1.14.6...1.14.7

[1.14.6]: https://github.com/Cray-HPE/csm-config/compare/1.14.5...1.14.6

[1.14.5]: https://github.com/Cray-HPE/csm-config/compare/1.14.4...1.14.5

[1.14.4]: https://github.com/Cray-HPE/csm-config/compare/1.14.3...1.14.4

[1.14.3]: https://github.com/Cray-HPE/csm-config/compare/1.14.2...1.14.3

[1.14.2]: https://github.com/Cray-HPE/csm-config/compare/1.14.1...1.14.2

[1.14.1]: https://github.com/Cray-HPE/csm-config/compare/1.14.0...1.14.1

[1.14.0]: https://github.com/Cray-HPE/csm-config/compare/1.13.0...1.14.0

[1.13.0]: https://github.com/Cray-HPE/csm-config/compare/1.12.0...1.13.0

[1.12.0]: https://github.com/Cray-HPE/csm-config/compare/1.11.0...1.12.0

[1.11.0]: https://github.com/Cray-HPE/csm-config/compare/1.10.1...1.11.0

[1.10.1]: https://github.com/Cray-HPE/csm-config/compare/1.10.0...1.10.1

[1.10.0]: https://github.com/Cray-HPE/csm-config/compare/1.9.0...1.10.0
