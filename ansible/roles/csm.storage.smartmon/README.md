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

This role runs on all the storage NCNs. It starts the SMART service, and reconfigures and redeploys
the running `node-exporter` (to use changed configurations, if any).

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

