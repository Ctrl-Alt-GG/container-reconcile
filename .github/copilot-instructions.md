# Container Reconcile Copilot Instructions

This repository uses Ansible to manage Proxmox LXC state with a strict role pipeline.

## Core Architecture
- Discovery first: proxmox_discovery gathers all shared facts.
- Mutation second: proxmox_reconcile consumes discovery facts and performs idempotent create or update.
- Reporting third: proxmox_report consumes discovery facts to render inventory output.

## Non-Negotiable Rules
- Authentication is per node only under inventory group vars proxmox_nodes.
- Do not reintroduce global proxmox_auth.
- Do not use direct REST calls with uri for Proxmox operations.
- Use community.proxmox modules only for Proxmox API access.
- Keep playbooks role-only. Do not add inline playbook tasks.
- Keep role tasks sequential and simple. Avoid block and rescue unless explicitly requested.
- Avoid noisy debug output. Prefer assert with clear fail messages.

## Networking Rules
- Bridge is configured per node.
- Prefix length is derived from subnet CIDR.
- Gateway is always excluded from allocatable addresses.
- Network and broadcast addresses are never allocatable hosts.

## Reconcile Behavior
- Match existing containers by hostname or name.
- Reuse existing VMID and IP for existing containers.
- Allocate VMID and IP only for new containers.
- Preserve deterministic selection and idempotency.

## Quality Bar
- Keep changes minimal and localized.
- Keep README and inventory examples aligned with behavior changes.
- When editing filter plugins, update and run tests in tests/test_filters.py.
