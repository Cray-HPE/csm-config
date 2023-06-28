csm.ims-passthrough
=========

IMS exposes several runtime and image customization job setup parameters to ansible through environment variables. These
variables can be treated like hints about expected hardware targets for an image (like architecture) in the case of
ambiguity when it is not immediately evident, or obfuscated by software based hardware emulation. These environment
variables are read as part of normal fact gathering, and can be accessed through the `ansible_vars` parent variable.
`set_fact` is not required to access them, however it may be desirable to do so when the variables are used frequently
throughout a playbook.

Exposing this information as environment variables during image customization allows us to cleanly abstract the image
customization process from more invasive methods, like custom ansible facts, or slower more scale-intensive approaches, 
like querying the IMS API for job information. Finally, this information is exposed to the running ansible job that 
needs it, and image customization jobs that do not require insight from these variables should not have to run these
tasks.

This role is not intended to be imported or used in a production playbook because of the added debug information is
unnecessary. It is, however, useful during debugging playbooks as a quick smoke test for IMS jail setup functionality.

Requirements
------------

Must be invoked in the context of an IMS image customization procedure. If associated role tasks are run during node
personalization, the exposed IMS variables will not be able to be read. Standard fact gathering is required to read this
information from the IMS image chroot environment.

Dependencies
------------

None.

Example Playbooks
----------------

    - hosts: Compute:Application:&cfs_image
      gather_facts: true
      roles:
         - role: csm.ims-passthrough

    - hosts: Compute:Application:&cfs_image
      gather_facts: true
      tasks:
        - name: Display IMS passthrough variables as captured through gathered facts
         [ Content Redacted; use csm.ims-passthrough/tasks/main.yml for the actual task definition]


License
-------

MIT

Author Information
------------------

Copyright 2023 Hewlett Packard Enterprise Development LP