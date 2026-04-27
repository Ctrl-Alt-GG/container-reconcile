---
applyTo: "playbooks/**/*.yml"
description: "Use when editing top-level playbooks; enforce role-only structure and execution order."
---
# Playbook Instructions

- Keep playbooks thin and role-oriented.
- Do not add inline tasks in playbooks.
- Provision order: discovery then reconcile.
- Report order: discovery then report.
- Keep gather_facts disabled unless explicitly needed.
