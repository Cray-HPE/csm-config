cf-cme-motd
=========

An Ansible role for installing a CA certificate onto the system.

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
- hosts: Management_Worker
  roles:
     - role: csm.ncn.ca_cert
```

License
-------

MIT

Author Information
------------------

Copyright 2022 Hewlett Packard Enterprise Development LP
