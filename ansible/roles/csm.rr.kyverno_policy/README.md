csm.rrs.kyverno_policy
======================

Apply kyverno policy and restart service

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
        # Apply kyverno policy and restart service
        - role: csm.rrs.kyverno_policy
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
