---
applyTo: "roles/proxmox_discovery/**/*.yml"
description: "Use when editing discovery role tasks, per-node API auth normalization, and shared fact collection for downstream roles."
---
# Discovery Role Instructions

- Treat discovery as the single source of runtime facts.
- Ensure every configured node is queried using that node credentials.
- Publish facts needed by both reconcile and report:
  - proxmox_nodes_discovered
  - proxmox_storage_usage
  - proxmox_containers
  - proxmox_all_vmids
  - proxmox_used_ips
  - proxmox_node_auth_map
- Keep tasks read-only and changed_when false for query modules.
- Keep data shapes stable to avoid downstream breakage.
