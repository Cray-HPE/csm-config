csm.gpg_keys
=========

Install the CSM GPG signing public key. This role is a dependency of the
`csm.packages` role.

Requirements
------------

The Kubernetes secret must be available in the namespace and field specified
by the `csm_gpg_key_*` variables below. The key must be stored as a base64-encoded
string.

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    csm_gpg_key_k8s_secret: "hpe-signing-key"

The Kubernetes secret which contains the GPG public key.

    csm_gpg_key_k8s_namespace: "services"

The Kubernetes namespace which contains the secret.

    csm_gpg_key_k8s_field: "gpg-pubkey"

The field in the Kubernetes secret that holds the GPG public key.

Dependencies
------------

None.

Example Playbook
----------------

    - hosts: Management_Master
      roles:
         - role: csm.gpg_key


License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP
