ntp
===============


An ansible role for installing /etc/chrony.conf

Requirements
------------

Tested on:

Role Variables
--------------

```yaml
ntp_server - ip address of ntp server

default: 10.2.0.1


```

Dependencies
------------

None.

Example Playbook
----------------

```yaml
    - hosts: Compute
      roles:
         - ntp
```

License
-------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP

Author Information
------------------

Inspiration
-----------

