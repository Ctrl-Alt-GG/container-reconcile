from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, Optional

import pytest

from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec


def _install_fallback_pulumi_module() -> None:
    try:
        importlib.import_module("pulumi")
        return
    except ModuleNotFoundError:
        pass

    module = ModuleType("pulumi")

    class Config:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def get(self, _key: str):
            return None

        def get_bool(self, _key: str):
            return None

    class RunError(Exception):
        pass

    class ResourceOptions:
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def export(_key: str, _value: Any) -> None:
        return None

    module.Config = Config
    module.RunError = RunError
    module.ResourceOptions = ResourceOptions
    module.export = export
    sys.modules["pulumi"] = module


def _install_fallback_pulumi_proxmoxve_module() -> None:
    # Always install the stub regardless of what is installed, to guarantee
    # that tests are isolated from the real pulumi_proxmoxve API and its
    # breaking changes across major versions.
    module = ModuleType("pulumi_proxmoxve")

    class _FakeArgs:
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class Container:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

    class ContainerCpuArgs(_FakeArgs):
        pass

    class ContainerMemoryArgs(_FakeArgs):
        pass

    class ContainerDiskArgs(_FakeArgs):
        pass

    class ContainerNetworkInterfaceArgs(_FakeArgs):
        pass

    class ContainerInitializationArgs(_FakeArgs):
        pass

    class ContainerInitializationIpConfigArgs(_FakeArgs):
        pass

    class ContainerInitializationIpConfigIpv4Args(_FakeArgs):
        pass

    class ContainerOperatingSystemArgs(_FakeArgs):
        pass

    class Provider:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

    module.Provider = Provider
    module.ct = SimpleNamespace(
        Container=Container,
        ContainerCpuArgs=ContainerCpuArgs,
        ContainerMemoryArgs=ContainerMemoryArgs,
        ContainerDiskArgs=ContainerDiskArgs,
        ContainerNetworkInterfaceArgs=ContainerNetworkInterfaceArgs,
        ContainerInitializationArgs=ContainerInitializationArgs,
        ContainerInitializationIpConfigArgs=ContainerInitializationIpConfigArgs,
        ContainerInitializationIpConfigIpv4Args=ContainerInitializationIpConfigIpv4Args,
        ContainerOperatingSystemArgs=ContainerOperatingSystemArgs,
    )
    sys.modules["pulumi_proxmoxve"] = module


_install_fallback_pulumi_module()
_install_fallback_pulumi_proxmoxve_module()


class FakePulumiConfig:
    def __init__(
        self,
        values: Optional[Dict[str, Any]] = None,
        bool_values: Optional[Dict[str, bool]] = None,
    ) -> None:
        self._values = values or {}
        self._bool_values = bool_values or {}

    def get(self, key: str) -> Any:
        return self._values.get(key)

    def get_bool(self, key: str) -> Optional[bool]:
        return self._bool_values.get(key)


@pytest.fixture
def make_fake_config():
    def _make(
        values: Optional[Dict[str, Any]] = None,
        bool_values: Optional[Dict[str, bool]] = None,
    ) -> FakePulumiConfig:
        return FakePulumiConfig(values=values, bool_values=bool_values)

    return _make


@pytest.fixture
def sample_host() -> HostSpec:
    return HostSpec(
        alias="hostA",
        ip="10.0.0.11",
        node_name="pve-node-a",
        datastore_id="local-lvm",
        bridge="vmbr0",
        endpoint="https://10.0.0.11:8006",
        insecure=False,
    )


@pytest.fixture
def sample_container() -> ContainerSpec:
    return ContainerSpec(
        name="app-1",
        host="hostA",
        template_file_id="local:vztmpl/ubuntu.tar.zst",
        vm_id=201,
        unprivileged=True,
        ip="10.0.0.101/24",
        gateway="10.0.0.1",
        cores=2,
        memory_mb=2048,
        disk_size_gb=8,
        os_type="ubuntu",
        hostname="app-1",
    )


@pytest.fixture
def sample_container_missing_vm() -> ContainerSpec:
    return ContainerSpec(
        name="app-2",
        host="hostA",
        template_file_id="local:vztmpl/ubuntu.tar.zst",
        vm_id=None,
        unprivileged=True,
        ip="dhcp",
        gateway=None,
        cores=2,
        memory_mb=2048,
        disk_size_gb=8,
        os_type="ubuntu",
        hostname="app-2",
    )


@pytest.fixture
def sample_deployment_spec(
    sample_host: HostSpec,
    sample_container: ContainerSpec,
    sample_container_missing_vm: ContainerSpec,
) -> DeploymentSpec:
    return DeploymentSpec(
        hosts={"hostA": sample_host},
        containers=[sample_container, sample_container_missing_vm],
    )


@pytest.fixture
def sample_raw_spec() -> Dict[str, Any]:
    return {
        "hosts": {
            "hostA": {
                "ip": "10.0.0.11",
                "node_name": "pve-node-a",
                "datastore_id": "local-lvm",
                "bridge": "vmbr0",
            }
        },
        "containers": [
            {
                "name": "app-1",
                "host": "hostA",
                "template_file_id": "local:vztmpl/ubuntu.tar.zst",
                "vm_id": 201,
                "ip": "10.0.0.101/24",
                "gateway": "10.0.0.1",
                "cores": 2,
                "memory_mb": 2048,
                "disk_size_gb": 8,
                "unprivileged": True,
                "os_type": "ubuntu",
                "hostname": "app-1",
            },
            {
                "name": "app-2",
                "host": "hostA",
                "template_file_id": "local:vztmpl/ubuntu.tar.zst",
            },
        ],
    }

