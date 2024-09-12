# csm.ncn.hsn_bonding

Configure a bonded HSN interface on an NCN.

## Requirements

* The Slingshot Fabric Manager Software is installed and the fabric has been configured.
  * A link aggregation group (LAG) has been created using the ports this node is connected to.
* The Slingshot Host Software is installed.
* The User Services Software is installed.

## Limitations

* Only one bonded interface is permitted per NCN.

## Role Variables

Available variables are listed below, along with default values (located in `defaults/main.yml`). These variables must be set on a per-host basis using a `host_vars` file.

| Variable         | Default Value                                                                          | Description                                                                      |
|------------------|----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| hsn_bond_enable  | false                                                                                  | Set to enable HSN NIC bonding on the node.                                       |
| hsn_bond_ip      | None. Value must be provided by Slingshot fabric administrator.                        | IP address to use for bond interface.                                            |
| hsn_bond_netmask | None. Value must be provided by Slingshot fabric administrator.                        | Netmask to use for bond interface.                                               |
| hsn_bond_mac     | None. Value must be provided by Slingshot fabric administrator.                        | MAC address to use for bond interface.                                           |
| hsn_bond_name    | "bond1"                                                                                | Name to assign the bond interface.                                               |
| hsn_bond_options | "mode=802.3ad xmit_hash_policy=layer2+3 miimon=100 ad_select=bandwidth lacp_rate=fast" | Options to be used for the bond interface.                                       |
| rt_tablenum      | 211                                                                                    | Number to assign the routing table used for the bond interface                   |
| rt_name          | "rt_{{hsn_bond_name}}"                                                                 | Name to assign the routing table used for the bond interface.                    |
| hsn_bond_devices | ["macvlan0","macvlan1"]                                                                | The names of the macvlan interfaces that will be assigned to the bond interface. |
| hsn_devices      | ["hsn0", "hsn1"]                                                                       | The names of the physical HSN interfaces that will be used for the bond.         |
| hsn_bond_sysctls | See defaults/main.yml                                                                  | The sysctl settings that will be applied to the bond interface.                  |

The `hsn_bond_ip`, `hsn_bond_netmask`, and `hsn_bond_mac` variables cannot be defaulted and must be set to values provided by the Slingshot fabric administrator.

There is a one to one mapping between `hsn_bond_devices` and `hsn_devices`. For example if the default values are used then the interface `mavlan0` will be assigned the `hsn0` interface 
and `macvlan1` will be assigned the `hsn1` interface.

## Dependencies

This playbook must be run after the `uss-ncn-integration` layer has run to ensure that the HSN interfaces have been configured.

## Example Playbook

    - hosts: Management_Worker:!cfs_image
      roles:
         - role: csm.ncn.hsn_bonding

License
-------

MIT

Author Information
------------------

Copyright 2024 Hewlett Packard Enterprise Development LP
