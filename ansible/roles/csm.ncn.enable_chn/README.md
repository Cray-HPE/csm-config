csm.ncn.enable_chn
==================

Configure the Customer Highspeed Network (CHN) IP addresses on worker nodes if applicable.

Requirements
------------

The system has been configured with CHN and it has been activated by setting it as the SystemDefaultRoute in the SLS BICAN network definition.

Role Variables
--------------

Available variables are listed below, along with default values (located in
`defaults/main.yml`):

    chn_interface: hsn0

The HSN interface to be used for the CHN.

Dependencies
------------

None.

Example Playbook
----------------

    - hosts: Management_Worker
      roles:
         - role: csm.ncn.enable_chn

License
-------

MIT

Author Information
------------------

Copyright 2021-2023 Hewlett Packard Enterprise Development LP
