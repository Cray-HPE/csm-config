localtime
===============


An ansible role for configuring localtime

Requirements
------------

Tested on:

Role Variables
--------------

```yaml
zoneinfo_file

default: /usr/share/zoneinfo/America/Chicago
The zoneinfo file to create a symlink to in /etc/localtime
Files are in /usr/share/zoneinfo

```

Dependencies
------------

None.

Example Playbook
----------------

```yaml
    - hosts: Compute
      roles:
         - localtime
```

License
-------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP

Author Information
------------------

Inspiration
-----------

