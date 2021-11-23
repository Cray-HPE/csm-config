csm.ncn.remove_from_etcd
=========

Safely removes an NCN from the baremetal etcd cluster if it is a member.

Requirements
------------

Requires the use of the `csi` tool, however the role will automatically download it if necessary.

Role Variables
--------------

None.

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- hosts: Management
  roles:
     - role: csm.ncn.remove_from_etcd
```

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP