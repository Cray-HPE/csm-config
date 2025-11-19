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
