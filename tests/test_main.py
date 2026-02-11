from __future__ import annotations

from pathlib import Path
import runpy

import pytest
import pulumi

import container_reconcile.infrastructure.config_reader as config_reader_module
import container_reconcile.infrastructure.spec_loader as spec_loader_module
import container_reconcile.services.container_args_factory as args_factory_module
import container_reconcile.services.deployment_service as deployment_module
import container_reconcile.services.spec_service as spec_service_module
from container_reconcile.domain.errors import SpecError


MAIN_PATH = Path(__file__).resolve().parents[1] / "__main__.py"


def test_main_wires_dependencies_and_runs_deployment_service(monkeypatch) -> None:
    capture = {}

    class StubConfigReader:
        pass

    class StubSpecLoader:
        pass

    class StubSpecService:
        pass

    class StubArgsFactory:
        pass

    class StubDeploymentService:
        def __init__(self, config_reader, spec_loader, spec_service, args_factory) -> None:
            capture["config_reader"] = config_reader
            capture["spec_loader"] = spec_loader
            capture["spec_service"] = spec_service
            capture["args_factory"] = args_factory

        def run(self) -> None:
            capture["ran"] = True

    monkeypatch.setattr(config_reader_module, "ConfigReader", StubConfigReader)
    monkeypatch.setattr(spec_loader_module, "SpecLoader", StubSpecLoader)
    monkeypatch.setattr(spec_service_module, "SpecService", StubSpecService)
    monkeypatch.setattr(args_factory_module, "ContainerArgsFactory", StubArgsFactory)
    monkeypatch.setattr(deployment_module, "DeploymentService", StubDeploymentService)

    runpy.run_path(str(MAIN_PATH), run_name="test_main_success")

    assert capture["ran"] is True
    assert isinstance(capture["config_reader"], StubConfigReader)
    assert isinstance(capture["spec_loader"], StubSpecLoader)
    assert isinstance(capture["spec_service"], StubSpecService)
    assert isinstance(capture["args_factory"], StubArgsFactory)


def test_main_translates_spec_error_to_run_error(monkeypatch) -> None:
    class StubConfigReader:
        pass

    class StubSpecLoader:
        pass

    class StubSpecService:
        pass

    class StubArgsFactory:
        pass

    class FailingDeploymentService:
        def __init__(self, config_reader, spec_loader, spec_service, args_factory) -> None:
            pass

        def run(self) -> None:
            raise SpecError("boom")

    class FakeRunError(Exception):
        pass

    monkeypatch.setattr(config_reader_module, "ConfigReader", StubConfigReader)
    monkeypatch.setattr(spec_loader_module, "SpecLoader", StubSpecLoader)
    monkeypatch.setattr(spec_service_module, "SpecService", StubSpecService)
    monkeypatch.setattr(args_factory_module, "ContainerArgsFactory", StubArgsFactory)
    monkeypatch.setattr(deployment_module, "DeploymentService", FailingDeploymentService)
    monkeypatch.setattr(pulumi, "RunError", FakeRunError)

    with pytest.raises(FakeRunError, match="boom"):
        runpy.run_path(str(MAIN_PATH), run_name="test_main_error")

