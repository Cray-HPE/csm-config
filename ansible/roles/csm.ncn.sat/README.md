csm.ncn.sat
===========

Configure the System Admin Toolkit (SAT) CLI on management non-compute nodes (NCNs).

Requirements
------------

This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with example values (located in
`defaults/main.yml` and `vars/main.yml`):

```yaml
sat_container_image_version_directory: "/opt/cray/etc/sat/"
```

The directory in which the file containing the `cray-sat` container image
version will be saved.

```yaml
sat_container_image_version_file: "version"
```

The file in which the `cray-sat` container image version will be saved.

```yaml
sat_config_file: "/root/.config/sat/sat.toml"
```

The location of the `sat.toml` configuration file, which will have its
permissions locked down.

```yaml
sat_container_image_version: "csm-latest"
```

The `cray-sat` container image version which will be written to the version
file described above. This variable is set correctly for the CSM version at CSM
installation time in `vars/main.yml`.

Dependencies
------------

None

Example Playbook
----------------

This example playbook configures SAT on the nodes in the groups `Management_Master` and
`Management_Worker`.

```yaml
- hosts:
  - Management_Master
  - Management_Worker
  roles:
  - role: csm.ncn.sat
```

License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP
