csm.packages
=========

Install CSM RPM repositories and packages.


Requirements
------------

None.

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    csm_sles_repositories: {}

List of SUSE Linux Enterprise Server repositories to install. See example below
for mapping keys. These keys are directly used with the Ansible `zypper_repository`
module. The `name`, `description`, `repo`, and `disable_gpg_check` fields are
supported.

    csm_sles_packages: []

List of packages to install.

Dependencies
------------

Requires the `csm.gpg_keys` role to be run to add the HPE GPG signing key to a
host's RPM database if the repository GPG checks are enabled (they are by
default, i.e. `disable_gpg_check: no`).

Example Playbook
----------------

    - hosts: Management_Master
      roles:
         - role: csm.packages
           vars:
             csm_sles_packages:
               - foo
               - bar
             csm_sles_repositories:
               - name: CSM SLE 15 SP2
                 description: CSM SUSE Linux Enterprise 15 SP2 Packages
                 repo: https://packages.local/repositories/csm-sle-15sp2
                 disable_gpg_check: no

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP
