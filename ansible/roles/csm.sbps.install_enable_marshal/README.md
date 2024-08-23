csm.sbps.install_enable_marshal
===============================

Install and enable/ start SBPS Marshal Agent (start systemd service) on specified NCN worker nodes.

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
        # Install and enable/ start SBPS Marshal Agent
        - role: csm.sbps.install_enable_marshal
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
