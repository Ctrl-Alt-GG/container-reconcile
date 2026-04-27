# Proxmox LXC Reconciler

Ansible playbooks that reconcile LXC containers on Proxmox to a desired state. Discovery gathers all facts first, then reconcile or report roles consume those facts.

## Prerequisites

- Ansible installed locally
- Proxmox VE cluster with API token access
- Python packages: `pip install -r requirements.txt`
- Ansible collections: `ansible-galaxy collection install -r requirements.yaml`

## Configuration

Edit [inventory/group_vars/all.yml](inventory/group_vars/all.yml):

```yaml
proxmox_nodes:
  - name: pve-01
    api_host: pve-01.example.com
    api_user: root@pam
    api_token_id: "{{ lookup('env', 'PROXMOX_PVE_01_TOKEN_ID', default='ansible') }}"
    api_token_secret: "{{ lookup('env', 'PROXMOX_PVE_01_TOKEN_SECRET', default='') }}"
    validate_certs: true
    storage_pools: [local-lvm, local]

ip_allocation:
  managed_subnets:
    - cidr: "10.0.1.0/24"
      gateway: "10.0.1.1"
      reserved_ips:
        - "10.0.1.1"     # gateway
```

Set per-node credentials via environment variables:

```bash
export PROXMOX_PVE_01_TOKEN_ID=ansible
export PROXMOX_PVE_01_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Define desired containers in [inventory/group_vars/containers.yml](inventory/group_vars/containers.yml):

```yaml
desired_containers:
  - name: web-01
    hostname: web-01
    memory_mb: 512
    cpu: 1
    disk_gb: 10
```

## Usage

**Provision containers** — creates or updates containers to match desired state:

```bash
ansible-playbook playbooks/provision_lxc.yml
```

**Report inventory** — read-only live inventory/status report:

```bash
ansible-playbook playbooks/report_lxc.yml
```

## How It Works

1. `proxmox_discovery` queries every node independently using that node's API auth.
2. Discovery publishes shared facts: node resources, storage pools, containers, used VMIDs, used IPs.
3. `proxmox_reconcile` uses only those facts to allocate and reconcile idempotently.
4. `proxmox_report` renders inventory/status from discovery facts.
