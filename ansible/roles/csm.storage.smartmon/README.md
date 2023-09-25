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
the running `node-exporter` if running from a node that has the ceph admin keyring which are nodes `ncn-s00[1-3]`.

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

