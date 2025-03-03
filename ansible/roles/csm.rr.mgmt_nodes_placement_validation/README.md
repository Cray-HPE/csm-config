csm.rr.mgmt_nodes_placement_validation
======================================

Do management nodes placement validation

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
        # Do management nodes placement validation
        - role: csm.rr.mgmt_nodes_placement_validation
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
