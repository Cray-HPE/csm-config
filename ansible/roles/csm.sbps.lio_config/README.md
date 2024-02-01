csm.sbps.lio_config
===================

Configure SBPS

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
      gather_facts: yes
      any_errors_fatal: true
      remote_user: root
      roles:
        # Configure SBPS
        - role: csm.sbps.lio_config
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
