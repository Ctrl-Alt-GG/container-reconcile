---
name: reconcile-idempotent
description: "Use when editing proxmox_reconcile allocation or mutation logic, including deterministic VMID and IP selection and idempotent create, update, skip behavior."
---
# Reconcile Idempotent Skill

## Use When
- You are editing reconcile task files.
- You are changing allocation rules.
- You are adjusting create or update behavior.

## Goals
- Consume discovery facts only.
- Keep deterministic placement and allocation.
- Preserve idempotency across repeated runs.

## Required Behavior
- Existing container: reuse VMID and IP.
- Missing container: allocate VMID and IP deterministically.
- Network IP allocation excludes network, broadcast, gateway, reserved, and used addresses.
- Use per-node bridge setting.

## Guardrails
- No extra discovery calls in reconcile.
- Prefer clear assert failures over debug noise.
