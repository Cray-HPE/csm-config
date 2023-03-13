rsyslog
===============


An ansible role for configuring rsyslog

Requirements
------------

Tested on:

Role Variables
--------------

```yaml
rsyslog_target

The hostname or IP address of the upstream rsyslog target or aggregator.

rsyslog_target_port

The port of the rsyslog aggregator

rsyslog_on_ncn

The rsyslog service should be managed on an NCN

rsyslog_enabled

The rsyslog service on an NCN's enable parameter setting.

rsyslog_state

The rsyslog service on an NCN's state parameter setting.
```

Dependencies
------------

None.

Example Playbook
----------------

```yaml
    - hosts: servers
      roles:
         - { role: rsyslog }
```

License
-------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP

Author Information
------------------

Inspiration
-----------

