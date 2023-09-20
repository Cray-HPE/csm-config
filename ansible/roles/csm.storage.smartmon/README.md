csm.storage.smartmon
=========

Start the SMART service; reconfigure and redeploy `node-exporter`.

Requirements
------------

None 

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

This role runs on all the storage NCNs. It starts the SMART service. It reconfigures and redeploys
the running `node-exporter` only on `mon[0]` which is `ncn-s001` (to use changed configurations,
if any). The ceph command to redeploy `node-exporter` can only be run from `ncn-s00[1-3]`.

```yaml
- hosts: Management_Storage
  any_errors_fatal: true
  remote_user: root
  roles:
     - role: csm.storage.smartmon
```

License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP

