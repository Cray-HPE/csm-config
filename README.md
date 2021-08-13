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
This repo uses some build helper scripts from the 
[cms-meta-tools](https://github.com/Cray-HPE/cms-meta-tools) repo. See that repo for more details.

## Local Builds
If you wish to perform a local build, you will first need to clone or copy the contents of the
cms-meta-tools repo to `./cms_meta_tools` in the same directory as the `Makefile`.

## Versioning
Use [SemVer](http://semver.org/). The version is located in the [.version](.version) file. At
build time, [Jenkinsfile.github](Jenkinsfile.github) generates the Docker version and Chart version
strings, and writes those to .docker_version and .chart_version respectively.

## Copyright and License
This project is copyrighted by Hewlett Packard Enterprise Development LP and is
under the MIT license. See the [LICENSE](LICENSE) file for details.

When making any modifications to a file that has a Cray/HPE copyright header,
that header must be updated to include the current year.

When creating any new files in this repo, if they contain source code, they must
have the HPE copyright and license text in their header, unless the file is
covered under someone else's copyright/license (in which case that should be in
the header). For this purpose, source code files include Dockerfiles, Ansible
files, RPM spec files, and shell scripts. It does **not** include Jenkinsfiles,
OpenAPI/Swagger specs, or READMEs.

When in doubt, provided the file is not covered under someone else's copyright
or license, then it does not hurt to add the HPE copyright to the header.
