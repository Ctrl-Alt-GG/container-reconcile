---
name: discovery-facts
description: "Use when editing or reviewing proxmox_discovery, per-node auth, fact normalization, or shared cluster fact contracts for reconcile and report."
---
# Discovery Facts Skill

## Use When
- You need to change how cluster facts are collected.
- You are touching roles/proxmox_discovery/tasks/main.yml.
- You need to add or adjust facts used by reconcile or report.

## Goals
- Keep discovery read-only.
- Query each node with that node authentication.
- Export stable facts for downstream roles.

## Required Outputs
- proxmox_nodes_discovered
- proxmox_storage_usage
- proxmox_containers
- proxmox_all_vmids
- proxmox_used_ips
- proxmox_node_auth_map

## Guardrails
- Use community.proxmox modules.
- Avoid uri module for Proxmox API.
- Keep changed_when false on query tasks.
