---
name: playbook-structure
description: "Use when editing top-level playbooks to preserve role-only structure and execution sequencing for provision and report flows."
---
# Playbook Structure Skill

## Use When
- You are modifying playbooks/provision_lxc.yml.
- You are modifying playbooks/report_lxc.yml.

## Goals
- Keep playbooks thin and readable.
- Keep orchestration in roles.

## Guardrails
- No inline tasks in playbooks.
- Provision flow order: discovery then reconcile.
- Report flow order: discovery then report.
