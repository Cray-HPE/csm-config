csm.ncn.standardize_hostnames
=========

Standardizes hostnames into the `ncn-XYYY` format that all other roles require. Most useful when included at the top 
of another role to guarantee that any and all utilities are in place before proceeding:

```yaml
- include_role:
    name: csm.ncn.standardize_hostnames
```

Requirements
------------

None.

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

```yaml
- hosts: Management
  roles:
     - role: csm.ncn.standardize_hostnames
```

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP