# Prepare Proxmox VE

Before running this project, gather the Proxmox details that map directly to the YAML and Pulumi config values.

## 1) Collect Required Infrastructure Values

You need these values from your Proxmox environment:

- **Endpoint URL**: typically `https://<proxmox-host-or-ip>:8006`
- **Node name**: the Proxmox node where containers will run (example: `pve-node-a`)
- **Datastore ID**: storage target for container disks (example: `local-lvm`)
- **Bridge name**: network bridge for container NICs (example: `vmbr0`)
- **Template file ID**: LXC template reference (example: `local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst`)

You will use:

- endpoint/auth in Pulumi config,
- node/datastore/bridge/template in `containers.yaml`.

## 2) Ensure an LXC Template Exists

Your `template_file_id` must exist in Proxmox before deployment.

Typical options:

- Upload/download template via Proxmox UI (`local` storage -> `CT Templates`).
- Use CLI tooling on Proxmox (for example `pveam`) to download templates.

If the template ID is wrong, deployment will fail during `pulumi up`.

## 3) Choose an API Authentication Method

Use one of these methods:

- API token (recommended)
- Username + password
- Auth ticket (+ optional CSRF token)

Recommended token format for Pulumi provider config:

- `user@realm!token-name=token-secret`

Example:

- `root@pam!pulumi=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## 4) TLS and Self-Signed Certificates

If your Proxmox endpoint uses a self-signed certificate, you will likely set:

- `proxmoxve:insecure true`

in Pulumi config (shown later in the guide).

## 5) VM ID Auto-Assignment Note

If you omit `vm_id` in `containers.yaml`, this program calls Proxmox `cluster/nextid` to assign IDs.

That means endpoint + auth must be valid even before resource creation starts.

## Next Step

Continue with [Set Up Project Locally](03-setup-project.md).

