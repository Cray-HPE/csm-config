csm.ncn.remove_from_kubernetes
=========

Safely removes an NCN from the Kubernetes cluster if it is a member.

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
     - role: csm.ncn.remove_from_kubernetes
```

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP