---
name: filter-test-quality
description: "Use when editing filter_plugins/proxmox_selectors.py or tests/test_filters.py for deterministic selection and allocation correctness."
---
# Filter and Test Quality Skill

## Use When
- You are editing selection helper filters.
- You are changing allocation semantics and need regression tests.

## Goals
- Keep helpers pure and deterministic.
- Use reliable standard library primitives.
- Maintain high-value unit coverage for edge cases.

## Validation
- Run pytest for tests/test_filters.py after changes.
