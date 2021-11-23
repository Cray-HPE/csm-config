csm.ncn.move_first_master
=========

The "first master" on Shasta is the one from which the rest of the join context is generated and copied from. In fact, 
it is a bit of a misnomer in that really any master after the very first bootstrap of the cluster is performed, but 
that is besides the point.

This role will perform all the necessary steps to (if necessary) copy this join context logic to another master node
that is *not* targeted for rebuild. 

Requirements
------------

Requires the use of the `csi` tool, however the role will automatically download it if necessary.

Role Variables
--------------

Available variables are listed below, along with default values (located in `defaults/main.yml`):

```yaml
authorization_header: "Bearer {{ token }}"
```

If necessary include an authorization header in the HTTP request (not necessary when running via CFS).

```yaml
kubeadm_config_location: "/etc/cray/kubernetes/kubeadm.yaml"
```

The location of the kubeadm config file on the NCN.

```yaml
join_command_location: "/etc/cray/kubernetes/join-command"
```

The desired location of the join command file.

```yaml
join_control_plane_command_location: "/etc/cray/kubernetes/join-command-control-plane"
```

The desired location of the join control plan command file.

```yaml
certificate_key_location: "/etc/cray/kubernetes/certificate-key"
```

The location of the certificate key file.

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- hosts: Management
  roles:
     - role: csm.ncn.move_first_master
```

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP