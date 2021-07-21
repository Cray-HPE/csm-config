csm.password
=========

Retrieve the password from the CSM vault instance and set it on the target host(s) for
the given user.

Requirements
------------

A password for the specified user must exist in the vault instance prior to
running this role. This role must be run in the context of the CSM Configuration
Framework Service (CFS) in its Ansible Execution Environment (AEE).

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    password_vault_url: 'http://cray-vault.vault:8200'

The address of the CSM Vault instance. This must be accessible to the AEE.

    password_vault_jwt_file: '/var/run/secrets/kubernetes.io/serviceaccount/token'

The Kubernetes JWT token file located in the pod running this role. This is
already in place when using AEE.

    password_vault_role_file: '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

The Kubernetes role file located in the pod running this role. This is already
in place when using AEE.

    password_vault_secret: 'secret/csm/management_nodes'

The secret in Vault that contains the key holding the password of the user.

    password_vault_secret_key: 'root_password'

The key in the `password_vault_secret` secret which contains the hashed password.

    password_username: 'root'

The username to set the hashed password on the target hosts.

Dependencies
------------

None

Example Playbook
----------------

While this role is meant for setting the `root` password, other user passwords
can be set by pointing to the correct locations in Vault as shown below:

    - hosts: Management
      roles:
         - { role: csm.password, password_username: foo, password_vault_secret_key: foo_password }

License
-------

MIT

Author Information
------------------

Copyright 2021 Hewlett Packard Enterprise Development LP
