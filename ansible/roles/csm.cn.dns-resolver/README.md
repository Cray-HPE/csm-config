### `external_dns_options`

`external_dns_options` is a list of customer-configurable fields to be added
to the `/etc/resolv.conf` DNS options list.

```yaml
external_dns_options: [ '' ]

# Example
external_dns_options:
  - 'single-request'
```

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- hosts: Compute
```