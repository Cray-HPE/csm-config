csm.rr.ceph_haproxy
==================

Update CEPH configuration and CEPH haproxy configuration on storage nodes (Utility Storage)

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
    - hosts: Management_Storage
      gather_facts: no
      any_errors_fatal: true
      remote_user: root
      roles:
        # Update CEPH configuration on storage nodes (Utility Storage)
        - role: csm.rr.ceph_haproxy
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
