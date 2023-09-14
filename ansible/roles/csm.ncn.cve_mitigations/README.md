ncn.cve_mitigations
=========

An Ansible role for applying CVE mitigations

Requirements
------------

None

Role Variables
--------------

None.

Dependencies
------------

cms-meta-tools

Example Playbook
----------------

```yaml
- hosts: "Management_Worker:!cfs_image"
  roles:
     - role: csm.ncn.cve-migitations
```

License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP
