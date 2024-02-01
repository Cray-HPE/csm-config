csm.sbps.mount_s3_images
========================

Mount s3 bucket 'boot-images' using s3fs read-only policy for SBPS agent

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
        # Mount s3 bucket 'boot-images' using s3fs read-only policy for SBPS agent
        - role: csm.sbps.mount_s3_images
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
