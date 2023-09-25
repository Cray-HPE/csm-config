csm.ims-remote
==================

Configure a compute image to be able to build IMS images

Requirements
------------

The system is able to access the `ims-remote-third-party` repo in Nexus.

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

```yaml
    builder_architecture: x86_64
```

The architecture of the compute node to be customized. 

```yaml
    kata_version: 2.5.1
```

The version of Kata to be downloaded.

Dependencies
------------

None.

Example Playbook
----------------

```yaml
   - hosts: Application:Compute
     gather_subset:
       - '!all'
       - '!min'
       - distribution
    any_errors_fatal: true
    remote_user: root
    roles:
      - role: csm.ims-remote
        vars:
          builder_architecture: "{{ ansible_env.IMS_ARCH |default('x86_64') }}"
```

License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP