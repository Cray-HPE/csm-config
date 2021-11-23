csm.ncn.download_utils
=========

Downloads any utils necessary to carry out NCN lifecycle events. Most useful when included at the top of another role
to guarantee that any and all utilities are in place before proceeding:

```yaml
- include_role:
    name: csm.ncn.download_utils
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
     - role: csm.ncn.download_utils
```

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP