from pathlib import Path

import pytest

from container_reconcile.domain.errors import SpecError
from container_reconcile.infrastructure.spec_loader import SpecLoader


def test_load_raises_when_file_does_not_exist(tmp_path: Path) -> None:
    loader = SpecLoader()
    missing = tmp_path / "missing.yaml"

    with pytest.raises(SpecError, match="was not found"):
        loader.load(str(missing))


def test_load_raises_for_empty_yaml(tmp_path: Path) -> None:
    loader = SpecLoader()
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    with pytest.raises(SpecError, match="is empty"):
        loader.load(str(path))


def test_load_raises_for_non_mapping_yaml(tmp_path: Path) -> None:
    loader = SpecLoader()
    path = tmp_path / "not_mapping.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(SpecError, match="must be a mapping"):
        loader.load(str(path))


def test_load_returns_mapping_for_valid_yaml(tmp_path: Path) -> None:
    loader = SpecLoader()
    path = tmp_path / "valid.yaml"
    path.write_text("hosts: {}\ncontainers: []\n", encoding="utf-8")

    loaded = loader.load(str(path))
    assert loaded == {"hosts": {}, "containers": []}

