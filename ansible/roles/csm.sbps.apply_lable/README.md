csm.sbps.apply_k8s_lable
========================

Apply k8s lable on intended worker nodes

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
        # Apply k8s lable on intended worker nodes
        - role: csm.sbps.apply_k8s_lable
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
