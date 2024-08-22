csm.sbps.enable_spire
=====================

Enable spire for SBPS Marshal Agent on specified NCN worker nodes.

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
        # Enable spire for SBPS Marshal Agent
        - role: csm.sbps.enable_spire
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
