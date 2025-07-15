csm.sbps.apply_label
========================

Add or remove Kubernetes label to worker nodes.

If the specified HSM group (specified by the `iscsi_group_name` variable) does not exist,
then all worker nodes should have the label.
If the specified HSM group exists, then only worker nodes that belong to that group should
have the label; all other worker nodes should not have the label.

This role determines which workers should have the label, determines which workers currently have
the label, and modifies things so that the current state matches the expected state.

Requirements
------------

None

Role Variables
--------------

| *Variable*          | *Description*       |
| ------------------- | ------------------- |
| `iscsi_group_name`  | Name of the HSM group that can be used to limit the iSCSI worker nodes (default: `iscsi_worker`)                          |
| `iscsi_label_value` | Value of the Kubernetes `iscsi` label that indicates a worker is intended to be used as an iSCSI target (default: `sbps`) |

Dependencies
------------

Example Playbook
----------------

```yaml
    - hosts: Management_Worker
      gather_facts: no
      any_errors_fatal: true
      remote_user: root
      vars:
        iscsi_group_name: "iscsi_worker"
        iscsi_label_value: "sbps"
      roles:
        # Apply k8s label on intended worker nodes
        - role: csm.sbps.apply_label
```

License
-------
None.

Author Information
------------------

Copyright 2024-2025 Hewlett Packard Enterprise Development LP
