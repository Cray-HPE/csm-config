csm.ncn.validate_plan
=========

Checks to see if *all* of the target NCNs were removed in any capacity (rebuild/reboot/shutdown) if the cluster would 
be left in a healthy state. Most useful when included at the top of another role to guarantee that any and all 
utilities are in place before proceeding:

```yaml
- include_role:
    name: csm.ncn.validate_plan
```

Requirements
------------

Requires the use of the `csi` tool, however the role will automatically download it if necessary.

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
     - role: csm.ncn.validate_plan
```

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP