csm.rr.check_enablement
=======================

Enable Rack Resiliency feature based on the site-init secret flag set

Requirements
------------

None.

Role Variables
--------------

`rr_enabled` is set to a boolean value based on whether RR is enabled or not.
If this variable is already set, then this role doesn't bother to re-set it.
Then, if RR is not enabled, then skip the rest of the current play.

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
        # Check if Rack Resiliency feature is enabled/ disabled
        - role: csm.rr.check_enablement
```

License
-------
None.

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
