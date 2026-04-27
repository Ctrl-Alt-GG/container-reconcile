---
applyTo: "inventory/**/*.yml"
description: "Use when editing inventory and group vars schema for nodes, networking, and desired containers."
---
# Inventory Instructions

- Authentication is defined per node in proxmox_nodes.
- Keep node fields explicit: name, api_host, api_user, api_token_id, api_token_secret, validate_certs, bridge, storage_pools.
- Keep managed subnet definitions CIDR-first.
- Do not duplicate prefix length outside CIDR.
- Gateway is always excluded by logic; reserved_ips should contain only additional exclusions.
- Keep examples realistic and internally consistent.
