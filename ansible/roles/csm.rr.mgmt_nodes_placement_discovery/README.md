csm.rr.mgmt_nodes_placement_discovery
=====================================

Do management nodes (master, worker and storage) placement discovery

Requirements
------------

None.

Role Variables
--------------

Dependencies
------------

Example Playbook
----------------

```yaml
    - hosts: Management_Master
      gather_facts: no
      any_errors_fatal: true
      remote_user: root
      roles:
        # Do management nodes (master, worker and storage) placement discovery
        - role: csm.rr.mgmt_nodes_placement_discovery
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
