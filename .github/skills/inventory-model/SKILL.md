---
name: inventory-model
description: "Use when editing inventory schema in inventory/group_vars for nodes, subnets, desired containers, and defaults alignment with role logic."
---
# Inventory Model Skill

## Use When
- You are changing group vars schema.
- You need to align examples with actual behavior.

## Goals
- Keep schema explicit and minimal.
- Keep per-node auth and bridge configuration clear.
- Keep subnet definitions CIDR-based.

## Guardrails
- Do not duplicate prefix length outside CIDR.
- Gateway exclusion is enforced by logic.
- Ensure examples match current reconcile behavior.
