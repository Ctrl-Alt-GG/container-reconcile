---
name: report-generation
description: "Use when editing proxmox_report tasks or templates/lxc_report.md.j2 for deterministic live inventory, node status, and storage reporting."
---
# Report Generation Skill

## Use When
- You are modifying report role behavior.
- You are editing report markdown template.

## Goals
- Keep reporting read-only.
- Consume discovery facts only.
- Keep report ordering deterministic.

## Guardrails
- Do not add drift-analysis sections.
- Do not add verbose runtime debug tasks.
