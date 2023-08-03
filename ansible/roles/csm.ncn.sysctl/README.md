csm.ncn.sysctl
=========

Set kernel parameter values with sysctl.

Requirements
------------

The values must exist in configuration prior to running this role. 
This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with example values (located in
`defaults/main.yml` and `vars/main.yml`):

```yaml
sysctl_config: 'dict'
```

The dictionary of the sysctl parameters and their values.

```yaml
sysctl_set: false
```

Whether to apply this in a running system and reload the values.

Dependencies
------------

None

Example Playbook
----------------

This role sets the kernel parameters in `/etc/sysctl.conf`. If `sysctl_set` is `true`, then
the role also ensures the parameters are written directly to the system with `systctl -w`.
Note that the playbook will not work with `sysctl_set` set to `true` if the system
is not running.
```yaml
    - hosts: Management
      roles:
        - role: csm.ncn.sysctl
          vars:
            sysctl_set: false
            sysctl_config:
              - name: net.ipv4.conf.all.accept_local
                value: 1
```
License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP
