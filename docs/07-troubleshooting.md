# Troubleshooting

Use this page when `pulumi preview` or `pulumi up` fails.

## Common Errors and Fixes

### `YAML file '...' was not found`

Cause:

- `container-reconcile:containersFile` points to the wrong path, or file is missing.

Fix:

- verify file location,
- or set config again:

```bash
pulumi config set container-reconcile:containersFile containers.yaml
```

### `YAML file '...' is empty`

Cause:

- `containers.yaml` exists but has no content.

Fix:

- add valid `hosts` and `containers` content.

### `Top-level key 'hosts' must be a non-empty mapping`
### `Top-level key 'containers' must be a non-empty list`

Cause:

- missing required top-level sections or empty structures.

Fix:

- ensure `hosts:` and `containers:` are present and non-empty.

### `containers[n].host must reference a defined host`

Cause:

- container refers to a host key that is not in `hosts`.

Fix:

- correct typo or add the missing host definition.

### `Duplicate container name ...`
### `Duplicate vm_id ...`

Cause:

- non-unique names or explicit VM IDs.

Fix:

- make values unique,
- or remove `vm_id` to auto-assign.

### `gateway cannot be set when ... ip is 'dhcp'`

Cause:

- `ip: dhcp` and `gateway` set together.

Fix:

- remove `gateway` for DHCP-based containers.

### `Field '...' must be a positive integer`

Cause:

- invalid values for `vm_id`, `cores`, `memory_mb`, or `disk_size_gb`.

Fix:

- use positive integer values only.

### `Proxmox endpoint is required for vm_id auto-allocation`

Cause:

- one or more containers omit `vm_id`, but endpoint/auth config is missing.

Fix:

- set endpoint and auth in Pulumi config (see [Configure Pulumi](04-configure-pulumi.md)).

### `Unable to authenticate for vm_id auto-allocation`

Cause:

- no usable auth method configured.

Fix:

- configure one auth method:
  - `proxmoxve:apiToken`, or
  - `proxmoxve:username` + `proxmoxve:password`, or
  - `proxmoxve:authTicket` (+ optional `proxmoxve:csrfPreventionToken`).

### `Failed to query Proxmox next-id`

Cause:

- endpoint not reachable, TLS mismatch, or auth problem.

Fix:

- verify endpoint URL and network reachability,
- verify credentials/token,
- set `proxmoxve:insecure true` for self-signed cert environments.

## Quick Diagnostics Commands

```bash
pulumi config
pulumi preview
pulumi stack output
```

If needed, re-check guide steps:

- [Install Prerequisites](01-install-prerequisites.md)
- [Prepare Proxmox VE](02-prepare-proxmox.md)
- [Set Up Project Locally](03-setup-project.md)
- [Configure Pulumi and Proxmox Access](04-configure-pulumi.md)
- [Write `containers.yaml`](05-write-containers-yaml.md)
- [Preview and Deploy](06-preview-and-deploy.md)

