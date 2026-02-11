from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from container_reconcile.domain.errors import SpecError


class SpecLoader:
    """Loads raw YAML deployment specification from disk."""

    def load(self, path: str) -> Dict[str, Any]:
        spec_path = Path(path)
        if not spec_path.exists():
            raise SpecError(
                f"YAML file '{path}' was not found. "
                "Set 'container-reconcile:containersFile' or create the file."
            )

        parsed = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if parsed is None:
            raise SpecError(f"YAML file '{path}' is empty.")
        if not isinstance(parsed, dict):
            raise SpecError("Top-level YAML content must be a mapping/object.")
        return parsed

