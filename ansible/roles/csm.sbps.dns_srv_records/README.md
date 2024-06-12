csm.sbps.dns_srv_records
========================

Configure SBPS DNS "SRV" and "A" records

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
    - hosts: Management_Worker
      gather_facts: no
      any_errors_fatal: true
      remote_user: root
      roles:
        # Configure SBPS DNS "SRV" and "A" records
        - role: csm.sbps.dns_srv_records
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
