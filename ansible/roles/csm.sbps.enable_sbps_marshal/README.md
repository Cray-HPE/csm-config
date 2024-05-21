csm.sbps.enable_sbps_marshal
============================

Enable SBPS Marshal agent (start systemd service) on specified NCN worker nodes.

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
        - role: csm.sbps.enable_sbps_marshal
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
