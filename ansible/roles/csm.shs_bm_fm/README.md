csm.shs_bm_fm
=============
Customize kubernetes base image and enable `ncn_nodes.yml` and `ncn-initrd.yml` for
supporting Fabric Manager nodes. Add repos for installing prerequisite 
OS RPMs required during Slingshot software installation.

Requirements
------------

None.

Role Variables
--------------
Available variables for Slingshot FabricManager Node are listed below:

* To configure repositories: `shs_bm_fm_repositories`.
* To blacklist kernel modules: `kernel_modules_blacklist`.
* To remove non-SLES RPMs: `remove_non_sles_rpms`.
* To remove files and directories : `remove_non_sles_paths`.
  
Dependencies
------------

Example Playbook
----------------

```yaml
    - hosts: Management_FabricManager
      gather_facts: no
      any_errors_fatal: true
      remote_user: root
      roles:
        - role: csm.shs_bm_fm 
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
