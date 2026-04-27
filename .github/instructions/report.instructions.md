---
applyTo: "roles/proxmox_report/**/*.yml,templates/lxc_report.md.j2"
description: "Use when editing report role or report template for live inventory and cluster status output."
---
# Report Instructions

- Report role must consume discovery facts and remain read-only.
- Do not reintroduce drift analysis sections.
- Keep rendered report deterministic and stable for diffs.
- Include inventory, node status, and storage status only.
- Avoid verbose runtime debug tasks.
