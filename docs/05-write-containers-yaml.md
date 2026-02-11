# Write `containers.yaml`

This file is the main input for the program.

## 1) Required Top-Level Structure

`containers.yaml` must contain:

- `hosts`: non-empty mapping
- `containers`: non-empty list

## 2) Host Schema

Each entry in `hosts` must include:

- `ip` (valid IP string)
- `node_name` (non-empty string)
- `datastore_id` (non-empty string)
- `bridge` (non-empty string)

Example:

```yaml
hosts:
  hostA:
    ip: 10.0.0.11
    node_name: pve-node-a
    datastore_id: local-lvm
    bridge: vmbr0
```

## 3) Container Schema

Each container in `containers` requires:

- `name` (non-empty string, unique)
- `host` (must reference a key in `hosts`)
- `template_file_id` (non-empty string)

Optional fields and defaults:

- `vm_id`: positive integer, unique if provided; omitted means auto-allocation from Proxmox `cluster/nextid`
- `unprivileged`: defaults to `true`
- `hostname`: defaults to `name`
- `ip`: defaults to `dhcp` (or CIDR like `10.0.0.101/24`)
- `gateway`: optional valid IP; **must not** be set when `ip: dhcp`
- `cores`: defaults to `1`
- `memory_mb`: defaults to `512`
- `disk_size_gb`: defaults to `8`
- `os_type`: defaults to `ubuntu`

## 4) Minimal Working Example

```yaml
hosts:
  hostA:
    ip: 10.0.0.11
    node_name: pve-node-a
    datastore_id: local-lvm
    bridge: vmbr0

containers:
  - name: app-1
    host: hostA
    template_file_id: local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst
```

In this minimal case:

- `vm_id` is auto-assigned
- networking defaults to DHCP
- CPU/memory/disk defaults are applied

## 5) Richer Example

```yaml
hosts:
  hostA:
    ip: 10.0.0.11
    node_name: pve-node-a
    datastore_id: local-lvm
    bridge: vmbr0

containers:
  - name: api-1
    host: hostA
    vm_id: 210
    template_file_id: local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst
    hostname: api-1
    os_type: ubuntu
    ip: 10.0.0.101/24
    gateway: 10.0.0.1
    cores: 2
    memory_mb: 2048
    disk_size_gb: 16
    unprivileged: true

  - name: worker-1
    host: hostA
    template_file_id: local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst
    ip: dhcp
```

## 6) Validation Rules You Should Know

- `host` must point to an existing host key.
- duplicate container names are rejected.
- duplicate explicit `vm_id` values are rejected.
- all integer sizing fields must be positive integers.
- whitespace-only strings are rejected for string-required fields.

## Next Step

Continue with [Preview and Deploy](06-preview-and-deploy.md).

