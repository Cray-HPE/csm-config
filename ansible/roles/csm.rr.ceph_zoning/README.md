csm.rr.ceph_zoning
==================

Apply CEPH zoning to storage nodes (Utility Storage)

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
        # Apply CEPH zoning to storage nodes (Utility Storage)
        - role: csm.rr.ceph_zoning
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
