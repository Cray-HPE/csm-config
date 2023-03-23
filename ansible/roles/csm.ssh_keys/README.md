csm.ssh_keys
=========

Retrieve the SSH keys from the CSM vault instance and copy them to the target
host(s) for the given user. The public key is also added to the `authorized_keys`
file.

Requirements
------------

A SSH key pair for the specified user must exist in the Vault instance prior to
running this role. This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    ssh_keys_vault_url: 'http://cray-vault.vault:8200'

The address of the CSM Vault instance. This must be accessible to the AEE.

    ssh_keys_vault_jwt_file: '/var/run/secrets/kubernetes.io/serviceaccount/token'

The Kubernetes JWT token file located in the pod running this role. This is
already in place when using AEE.

    ssh_keys_vault_role_file: '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

The Kubernetes role file located in the pod running this role. This is already
in place when using AEE.

    ssh_keys_user_private_key_secret_prefix: 'secret/csm/users/'

The secret in Vault that contains the value holding the private portion of the
SSH keypair of the user. This value *must* end with a `/`. The full secret is
constructed as `ssh_keys_user_private_key_secret_prefix` + `ssh_keys_username`.

    ssh_keys_user_private_key_key: 'ssh_private_key'

The field in the `ssh_keys_user_private_key_secret` secret which contains the SSH
private key.

    ssh_keys_user_public_key_secret_prefix: 'secret/csm/users/'

The secret in Vault that contains the value holding the public portion of the
SSH keypair of the user. This value *must* end with a `/`. The full secret is
constructed as `ssh_keys_user_public_key_secret_prefix` + `ssh_keys_username`.

    ssh_keys_user_public_key_key: 'ssh_public_key'

The field in the `ssh_keys_user_public_key_key` secret which contains the SSH
public key.

    ssh_keys_username: 'root'

The user account name which owns the SSH keypair to be placed on the target hosts.

    ssh_keys_keytype: 'rsa'

The ssh keypair key type. This is only used when naming the files that are copied.
Private keys will be `id_{{ssh_keys_keytype}}` and public keys will be
`id_{{ssh_keys_keytype}}.pub`.

Dependencies
------------

None

Example Playbook
----------------

While this role sets the `root` user keys by default on CSM management nodes,
other user's keys can be set by pointing to different locations in Vault. If the
keys are located in Vault at `secrets/csm/users/foo:ssh_private_key` and
`secrets/csm/users/foo:ssh_public_key`, the role is invoked as shown below for
the `foo` user with RSA-type keys:

    - hosts: Management
      roles:
         - role: csm.ssh_keys
           vars:
             ssh_keys_username: foo

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP
