from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import container_reconcile.services.deployment_service as deployment_module
from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec
from container_reconcile.services.deployment_service import DeploymentService


def _build_spec(vm_id: int | None) -> DeploymentSpec:
    host = HostSpec(
        alias="hostA",
        ip="10.0.0.11",
        node_name="pve-node-a",
        datastore_id="local-lvm",
        bridge="vmbr0",
    )
    container = ContainerSpec(
        name="app-1",
        host="hostA",
        template_file_id="local:vztmpl/ubuntu.tar.zst",
        vm_id=vm_id,
        unprivileged=True,
        ip="dhcp",
        gateway=None,
        cores=1,
        memory_mb=512,
        disk_size_gb=8,
        os_type="ubuntu",
        hostname="app-1",
    )
    return DeploymentSpec(hosts={"hostA": host}, containers=[container])


def test_run_creates_resources_and_exports_without_nextid_path(monkeypatch) -> None:
    config_reader = Mock()
    spec_loader = Mock()
    spec_service = Mock()
    args_factory = Mock()
    spec = _build_spec(vm_id=301)

    config_reader.get_containers_file.return_value = "containers.yaml"
    spec_loader.load.return_value = {"hosts": {}, "containers": []}
    spec_service.to_deployment_spec.return_value = spec
    args_factory.build.return_value = {"node_name": "pve-node-a", "vm_id": 301}
    args_factory.resource_name_for.return_value = "lxc-1-app-1"

    created_resource = object()
    container_ctor = Mock(return_value=created_resource)
    monkeypatch.setattr(
        deployment_module,
        "proxmoxve",
        SimpleNamespace(ct=SimpleNamespace(Container=container_ctor)),
    )

    exports = []
    monkeypatch.setattr(
        deployment_module.pulumi,
        "export",
        lambda key, value: exports.append((key, value)),
    )

    nextid_client_cls = Mock()
    vm_allocator_cls = Mock()
    monkeypatch.setattr(deployment_module, "ProxmoxNextIdClient", nextid_client_cls)
    monkeypatch.setattr(deployment_module, "VmIdAllocator", vm_allocator_cls)

    service = DeploymentService(
        config_reader=config_reader,
        spec_loader=spec_loader,
        spec_service=spec_service,
        args_factory=args_factory,
    )
    service.run()

    nextid_client_cls.assert_not_called()
    vm_allocator_cls.assert_not_called()
    container_ctor.assert_called_once_with("lxc-1-app-1", node_name="pve-node-a", vm_id=301)

    export_map = dict(exports)
    assert export_map["yaml_file"] == "containers.yaml"
    assert export_map["container_count"] == 1
    assert export_map["container_names"] == ["app-1"]
    assert export_map["container_vm_ids"] == {"app-1": 301}
    assert export_map["container_hosts"] == {"app-1": "hostA"}


def test_run_uses_nextid_allocator_when_vm_id_is_missing(monkeypatch) -> None:
    config_reader = Mock()
    spec_loader = Mock()
    spec_service = Mock()
    args_factory = Mock()
    spec = _build_spec(vm_id=None)
    connection = object()

    config_reader.get_containers_file.return_value = "containers.yaml"
    config_reader.get_proxmox_connection_config.return_value = connection
    spec_loader.load.return_value = {"hosts": {}, "containers": []}
    spec_service.to_deployment_spec.return_value = spec
    args_factory.build.side_effect = (
        lambda container, host: {"node_name": host.node_name, "vm_id": container.vm_id}
    )
    args_factory.resource_name_for.return_value = "lxc-1-app-1"

    capture = {}

    class FakeNextIdClient:
        def __init__(self, cfg) -> None:
            capture["cfg"] = cfg

    class FakeAllocator:
        def __init__(self, client) -> None:
            capture["client"] = client

        def allocate(self, deployment_spec: DeploymentSpec) -> None:
            capture["allocated"] = True
            deployment_spec.containers[0].vm_id = 444

    container_ctor = Mock(return_value=object())
    monkeypatch.setattr(
        deployment_module,
        "proxmoxve",
        SimpleNamespace(ct=SimpleNamespace(Container=container_ctor)),
    )
    monkeypatch.setattr(deployment_module, "ProxmoxNextIdClient", FakeNextIdClient)
    monkeypatch.setattr(deployment_module, "VmIdAllocator", FakeAllocator)

    exports = []
    monkeypatch.setattr(
        deployment_module.pulumi,
        "export",
        lambda key, value: exports.append((key, value)),
    )

    service = DeploymentService(
        config_reader=config_reader,
        spec_loader=spec_loader,
        spec_service=spec_service,
        args_factory=args_factory,
    )
    service.run()

    assert capture["cfg"] is connection
    assert capture["allocated"] is True
    container_ctor.assert_called_once_with("lxc-1-app-1", node_name="pve-node-a", vm_id=444)
    assert dict(exports)["container_vm_ids"] == {"app-1": 444}

