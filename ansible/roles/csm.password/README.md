csm.password
=========

Retrieve the password from the CSM vault instance and set it on the target
host(s) for the given user.

Requirements
------------

A password for the specified user must exist in the vault instance prior to
running this role. If the password does not exist, the role will exit cleanly
and make no changes to the target host(s). This role must be run in the context
of the CSM Configuration Framework Service (CFS) in its Ansible Execution
Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    password_vault_url: 'http://cray-vault.vault:8200'

The address of the CSM Vault instance. If a non-CSM Vault instance is used, it
must be accessible to the AEE.

    password_vault_jwt_file: '/var/run/secrets/kubernetes.io/serviceaccount/token'

The Kubernetes JWT token file located in the pod running this role. This is
already in place when using AEE.

    password_vault_role_file: '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

The Kubernetes role file located in the pod running this role. This is already
in place when using AEE.

    password_vault_secret_prefix: 'secret/csm/users/'

The secret in Vault that contains the key holding the password of the user. The
full secret will be `password_vault_secret_prefix` + `password_username`.
This value *must* end with a `/`.

    password_vault_secret_key: 'password'

The field in the `password_vault_secret` secret which contains the hashed password.

    password_username: 'root'

The username to set the hashed password on the target hosts.

Dependencies
------------

None

Example Playbook
----------------

While this role sets the `root` user password by default, other user passwords
can be set by pointing to the correct locations in Vault as shown below:

    - hosts: Management
      roles:
         - role: csm.password
           vars:
             password_username: foo

Set this user's password in Vault with the following:

    vault write secret/csm/users/foo password='.....'

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP
