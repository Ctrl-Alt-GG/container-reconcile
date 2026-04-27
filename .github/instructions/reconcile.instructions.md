---
applyTo: "roles/proxmox_reconcile/**/*.yml"
description: "Use when editing reconcile logic for deterministic node, storage, VMID, and IP selection and idempotent create or update behavior."
---
# Reconcile Role Instructions

- Consume discovery facts only. Do not add extra fact-gathering API calls.
- Preserve deterministic allocation order.
- Existing containers reuse discovered VMID and IP.
- New containers get first available VMID and first allocatable IP.
- Always exclude gateway, network, and broadcast from allocations.
- Bridge comes from selected node configuration.
- Prefix length comes from subnet CIDR.
- Keep actions idempotent: create, update, or skip.
- Keep failures explicit with assert messages.
