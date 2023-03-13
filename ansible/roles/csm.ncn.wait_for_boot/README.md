csm.ncn.wait_for_boot
=========

When rebuilding a node there are a number of tasks that node must take before it is considered to have rejoined the 
cluster. This role waits for each of them to be true in chronological order. For example, a node must request its 
bootscript from BSS before it can be expected to have requested its cloud-init config. 

Requirements
------------

Requires the use of the `csi` tool, however the role will automatically download it if necessary.

Role Variables
--------------

Available variables are listed below, along with default values (located in `defaults/main.yml`):

```yaml
wait_for_retries: 200
```

The number of times to retry any blocking action.

```yaml
wait_for_delay: 5
```

The delay between retries for any blocking action.

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- hosts: Management
  roles:
     - role: csm.ncn.wait_for_boot
```

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP