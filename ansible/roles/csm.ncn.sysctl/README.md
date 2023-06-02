csm.ncn.sysctl
=========

Set sysctl values.

Requirements
------------

The sysctl values must exist in configuration prior to running this role. 
This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    sysctl_config: 'dict'

The dict of the sysctl parameters and their values

Dependencies
------------

None

Example Playbook
----------------

This role sets the sysctl values in /etc/sysctl.conf and ensures the
values are currently set by writing directly with systctl -w).
The role is invoked as shown below for the `foo` user with RSA-type keys:

    - hosts: Management
      roles:
        - role: csm.ncn.sysctl
          vars:
            sysctl_config:
              - name: net.ipv4.conf.all.accept_local
                value: 1

License
-------

MIT

Author Information
------------------

Copyright 2021-2024 Hewlett Packard Enterprise Development LP
