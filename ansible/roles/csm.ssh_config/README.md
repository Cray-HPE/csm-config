csm.ssh_config
=========

Retrieve the SSH configuration from the CSM vault instance and copy it to the target
host(s) for the given user.

See also the related `csm.ssh_keys` and `csm.password` roles.

Requirements
------------

A SSH configuration for the specified user must exist in the Vault instance prior to
running this role. This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    ssh_config_vault_url: 'http://cray-vault.vault:8200'

The address of the CSM Vault instance. This must be accessible to the AEE.

    ssh_config_vault_jwt_file: '/var/run/secrets/kubernetes.io/serviceaccount/token'

The Kubernetes JWT token file located in the pod running this role. This is
already in place when using AEE.

    ssh_config_vault_role_file: '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

The Kubernetes role file located in the pod running this role. This is already
in place when using AEE.

    ssh_config_user_config_secret_prefix: 'secret/csm/users/'

The secret in Vault that contains the value holding the SSH configuration
of the user. This value *must* end with a `/`. The full secret is
constructed as `ssh_config_user_config_secret_prefix` + `ssh_config_username`.

    ssh_config_user_config_key: 'ssh_config'

The field in the secret which contains the SSH configuration.

    ssh_config_username: 'root'

The user account name which owns the SSH configuration to be placed on the target hosts.

    ssh_config_filename: 'config'

The name of the file for the SSH configuration. The full path is
`{{ user home directory }}/.ssh/{{ ssh_config_filename }}`

Dependencies
------------

None

Example Playbook
----------------

While this role sets the `root` user SSH configuration by default on CSM management nodes,
other user's configurations can be set by pointing to different locations in Vault. If the
configuration is located in Vault at `secrets/csm/users/foo:ssh_config`, the role is invoked
as shown below for the `foo` user:

    - hosts: Management
      roles:
         - role: csm.ssh_config
           vars:
             ssh_config_username: foo

License
-------

MIT

Author Information
------------------

Copyright 2025 Hewlett Packard Enterprise Development LP
