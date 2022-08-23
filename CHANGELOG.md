# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.13.0] - 2022-08-23
### Changed
- enabling the embedded repos on the ncns

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
