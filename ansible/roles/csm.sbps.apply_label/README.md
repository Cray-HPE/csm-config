csm.sbps.apply_k8s_label
========================

Apply k8s label on intended worker nodes

Requirements
------------

ansible_hostname must be set (`gather_subset: min`)

Role Variables
--------------

| *Variable*          | *Description*       |
| ------------------- | ------------------- |
| `iscsi_group_name`  | Name of the HSM group that can be used to limit the iSCSI worker nodes (default: `iscsi_worker`)                           |
| `iscsi_label_value` | Value of the Kubernetes `iscsi` label trhat indicates a worker is intended to be used as an iSCSI target (default: `sbps`) |

Dependencies
------------

Example Playbook
----------------

```yaml
    - hosts: Management_Worker
      gather_facts: yes
      # We need to get ansible_hostname set
      gather_subset: min
      any_errors_fatal: true
      remote_user: root
      vars:
        iscsi_group_name: "iscsi_worker"
        iscsi_label_value: "sbps"
      roles:
        # Apply k8s label on intended worker nodes
        - role: csm.sbps.apply_k8s_label
```

License
-------
None.

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
