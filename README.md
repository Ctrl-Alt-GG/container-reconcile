Pulumi Python program that creates Proxmox LXC containers from a single YAML file.

## Start Here

Follow this guide set if you want end-to-end setup from a machine that already has Git and Python installed:

- [Guide Index](docs/00-start-here.md)
- [Install Pulumi CLI](docs/01-install-prerequisites.md)
- [Prepare Proxmox VE](docs/02-prepare-proxmox.md)
- [Set Up Project Locally](docs/03-setup-project.md)
- [Configure Pulumi and Proxmox Access](docs/04-configure-pulumi.md)
- [Write `containers.yaml`](docs/05-write-containers-yaml.md)
- [Preview and Deploy](docs/06-preview-and-deploy.md)
- [Troubleshooting](docs/07-troubleshooting.md)

## What It Does

- Reads one YAML file with two sections: `hosts` and `containers`.
- Validates host/container definitions before creating resources.
- Creates `proxmoxve.ct.Container` resources with explicit host mapping.
- Supports optional `vm_id`:
  - If omitted, the program queries Proxmox `cluster/nextid` and assigns IDs sequentially.
- Supports optional `unprivileged`:
  - If omitted, defaults to `true`.

## Prerequisites

- Python 3.10+
- Pulumi CLI
- Access to a Proxmox VE API endpoint

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pulumi stack init dev
```

## Provider Configuration

Set Proxmox provider config in Pulumi (credentials should be secrets):

```bash
pulumi config set proxmoxve:endpoint https://proxmox.example.internal:8006
pulumi config set --secret proxmoxve:apiToken 'root@pam!pulumi=TOKEN_SECRET'
pulumi config set proxmoxve:insecure true
```

Alternative auth is also supported by the provider:

- `proxmoxve:username` + `proxmoxve:password`
- `proxmoxve:authTicket` (+ optional `proxmoxve:csrfPreventionToken`)

The program reuses these values to authenticate the `nextid` API call for automatic `vm_id` assignment.

## Program Config

The YAML input path is configurable:

```bash
pulumi config set container-reconcile:containersFile containers.yaml
```

Optional overrides for the `nextid` API call (usually not needed if provider config is set):

- `container-reconcile:proxmoxEndpoint`
- `container-reconcile:proxmoxInsecure`
- `container-reconcile:proxmoxApiToken`
- `container-reconcile:proxmoxUsername`
- `container-reconcile:proxmoxPassword`
- `container-reconcile:proxmoxOtp`
- `container-reconcile:proxmoxAuthTicket`
- `container-reconcile:proxmoxCsrfToken`

## Code Architecture

The program is organized into OOP-focused layers:

- `domain`
  - `errors.py`: domain exception types (`SpecError`)
  - `models.py`: typed spec models (`HostSpec`, `ContainerSpec`, `DeploymentSpec`)
  - `validators.py`: reusable field validation helpers
- `infrastructure`
  - `spec_loader.py`: YAML file loading
  - `config_reader.py`: Pulumi/app config resolution with precedence
  - `proxmox_nextid_client.py`: Proxmox API auth and `cluster/nextid` calls
- `services`
  - `spec_service.py`: validation + normalization from raw YAML into typed models
  - `vm_id_allocator.py`: sequential VM ID assignment for missing `vm_id`
  - `container_args_factory.py`: maps domain models to `proxmoxve.ct.Container` args
  - `deployment_service.py`: orchestration of load/validate/allocate/deploy/export
- `__main__.py`
  - thin composition root that wires services and surfaces `SpecError` as `pulumi.RunError`

## YAML Schema

`containers.yaml` must contain:

- `hosts`: mapping keyed by host alias.
- `containers`: list of container definitions.

### Required host fields

- `ip`: host management IP.
- `node_name`: Proxmox node name.
- `datastore_id`: datastore for container disks.
- `bridge`: network bridge (for example `vmbr0`).

### Required container fields

- `name`
- `host` (must reference a key in `hosts`)
- `template_file_id`

### Optional container fields

- `vm_id` (auto-assigned when omitted)
- `unprivileged` (defaults to `true`)
- `hostname` (defaults to `name`)
- `ip` (defaults to `dhcp`; accepts CIDR like `10.0.0.101/24` or `dhcp`)
- `gateway`
- `cores` (defaults to `1`)
- `memory_mb` (defaults to `512`)
- `disk_size_gb` (defaults to `8`)
- `os_type` (defaults to `ubuntu`)

## Example Input

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
    ip: 10.0.0.101/24
    gateway: 10.0.0.1
    cores: 2
    memory_mb: 2048
    disk_size_gb: 8
    # vm_id omitted -> auto-assigned using cluster/nextid
    # unprivileged omitted -> defaults to true

  - name: app-2
    host: hostA
    vm_id: 210
    template_file_id: local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst
    unprivileged: false
```

## Run

```bash
pulumi preview
pulumi up
```

## Run Tests

Install dev dependencies and run tests:

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite is fully isolated and does not require:

- a real Pulumi stack initialization,
- a real Proxmox endpoint,
- outbound network access.

## Outputs

The stack exports:

- `yaml_file`
- `container_count`
- `container_names`
- `container_vm_ids`
- `container_hosts`
