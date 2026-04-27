---
applyTo: "filter_plugins/**/*.py,tests/**/*.py"
description: "Use when editing filter plugins or tests for deterministic allocation logic and CIDR host handling."
---
# Python and Tests Instructions

- Keep filter functions pure and deterministic.
- Prefer standard library primitives for correctness, such as ipaddress.
- Add or update tests when allocation behavior changes.
- Keep tests focused on deterministic outcomes and edge cases.
- Maintain Python type hints and simple, readable code.
