---
applyTo: ".github/workflows/*.yml,.github/workflows/*.yaml"
description: "Use when editing CI workflows; this repository keeps CI limited to linting and pytest."
---
# Workflow Instructions

- Keep CI minimal: lint plus tests only.
- Do not add external paid security scanners unless explicitly requested.
- Keep workflow Python versions aligned with project support.
- Prefer fast feedback and clear job naming.
