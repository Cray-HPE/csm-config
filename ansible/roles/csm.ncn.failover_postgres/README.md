csm.ncn.failover_postgres
=========

Forces the leader Postgres instance away from any target NCN. Does this by computing a list of all the clusters and
then reaches out to the Patroni API to facilitate the failover action if necessary.

Requirements
------------

None.

Role Variables
--------------

None

Dependencies
------------

Requires the use of the `csi` tool, however the role will automatically download it if necessary.

Example Playbook
----------------

```yaml
- hosts: Management
  roles:
     - role: csm.ncn.failover_postgres
```

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP