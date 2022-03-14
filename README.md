# csm-config

Cray System Management (CSM) Ansible roles and playbooks. Use these playbooks
to configure and personalize non-compute nodes (NCNs) and configure CSM
software on other node types (including compute nodes, UANs, etc).

## Playbooks

* `site.yml` -- top-level CSM play defining all of the CSM infrastructure.
  Includes host group-specific top level plays for CSM node types (master,
  workers, etc).
* `ncn-*_nodes.yml` -- top-level role-specific NCN plays.

All other plays are task-specific and may span multiple NCN host groups.

## Roles

Roles are defined in the `ansible/roles` directory and should be prefixed with
`csm.` for their naming convention.

## Variables

Variables should typically be defined by default in role default files, or by
the user in group/host inventory. In the rare occasion these two do not meet
meet the use case, the `vars` directory can be included.

### Configuring CSM RPM Repositories and Installing Packages

CSM repositories to be added to the system should be specified in the
`ansible/vars/csm_repos.yml` file.

CSM packages to be installed on systems should be specified in the
`ansible/vars/csm_packages.yml` file.

## Build Helpers
This repo uses some build helpers from the 
[cms-meta-tools](https://github.com/Cray-HPE/cms-meta-tools) repo. See that repo for more details.

## Local Builds
If you wish to perform a local build, you will first need to clone or copy the contents of the
cms-meta-tools repo to `./cms_meta_tools` in the same directory as the `Makefile`. When building
on github, the cloneCMSMetaTools() function clones the cms-meta-tools repo into that directory.

For a local build, you will also need to manually write the .version, .docker_version (if this repo
builds a docker image), and .chart_version (if this repo builds a helm chart) files. When building
on github, this is done by the setVersionFiles() function.

## Versioning
The version of this repo is generated dynamically at build time by running the version.py script in 
cms-meta-tools. The version is included near the very beginning of the github build output. 

In order to make it easier to go from an artifact back to the source code that produced that artifact,
a text file named gitInfo.txt is added to Docker images built from this repo. For Docker images,
it can be found in the / folder. This file contains the branch from which it was built and the most
recent commits to that branch. 

For helm charts, a few annotation metadata fields are appended which contain similar information.

For RPMs, a changelog entry is added with similar information.

## New Release Branches
When making a new release branch:
    * Be sure to set the `.x` and `.y` files to the desired major and minor version number for this repo for this release. 
    * If an `update_external_versions.conf` file exists in this repo, be sure to update that as well, if needed.

## Copyright and License
This project is copyrighted by Hewlett Packard Enterprise Development LP and is
under the MIT license. See the [LICENSE](LICENSE) file for details.

