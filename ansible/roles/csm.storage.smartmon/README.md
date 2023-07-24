csm.storage.smartmon
=========

Start the smart service, reconfigure and redeploy node_exporter.

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

This role starts the smart service on all the storage nodes and reconfigures and redeploys the running node_exporter with new applied configurations. 

```yaml
- hosts: Management
  roles:
     - role: csm.storage.smartmon
```
License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP

