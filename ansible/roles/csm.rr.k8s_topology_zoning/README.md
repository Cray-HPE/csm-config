csm.rr.k8s_topology_zoning
==========================

Apply k8s topology zoning to Master and Worker nodes

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
        # Run k8s topology zoning on one of the Master node to apply k8s topology zoning
        # to Master and Worker nodes
        - role: csm.rr.k8s_topology_zoning
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
