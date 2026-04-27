---
name: ci-lint-tests
description: "Use when editing GitHub Actions workflows to keep CI focused on lint and pytest with minimal external dependencies."
---
# CI Lint and Tests Skill

## Use When
- You are editing files in .github/workflows.

## Goals
- Keep CI simple and fast.
- Preserve lint and pytest checks.

## Guardrails
- Avoid adding unrelated deployment or security products unless explicitly requested.
- Keep workflow steps readable and deterministic.
