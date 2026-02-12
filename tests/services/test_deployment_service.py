from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import container_reconcile.services.deployment_service as deployment_module
from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec
from container_reconcile.services.deployment_service import DeploymentService


def _host(alias: str = "hostA", ip: str = "10.0.0.11") -> HostSpec:
    return HostSpec(
        alias=alias,
        ip=ip,
        node_name=f"pve-{alias}",
        datastore_id="local-lvm",
        bridge="vmbr0",
        endpoint=f"https://{ip}:8006",
        insecure=False,
    )


def _container(
    name: str = "app-1",
    host: str = "hostA",
    vm_id: int | None = None,
) -> ContainerSpec:
    return ContainerSpec(
        name=name,
        host=host,
        template_file_id="local:vztmpl/ubuntu.tar.zst",
        vm_id=vm_id,
        unprivileged=True,
        ip="dhcp",
        gateway=None,
        cores=1,
        memory_mb=512,
        disk_size_gb=8,
        os_type="ubuntu",
        hostname=name,
    )


def _build_spec(vm_id: int | None) -> DeploymentSpec:
    return DeploymentSpec(
        hosts={"hostA": _host()},
        containers=[_container(vm_id=vm_id)],
    )


def test_run_creates_resources_with_per_host_provider(monkeypatch) -> None:
    config_reader = Mock()
    spec_loader = Mock()
    spec_service = Mock()
    args_factory = Mock()
    spec = _build_spec(vm_id=301)
    connection = SimpleNamespace(
        endpoint="https://10.0.0.11:8006",
        insecure=False,
        api_token="TOKEN",
        username=None,
        password=None,
    )

    config_reader.get_containers_file.return_value = "containers.yaml"
    config_reader.get_host_connection_config.return_value = connection
    spec_loader.load.return_value = {"hosts": {}, "containers": []}
    spec_service.to_deployment_spec.return_value = spec
    args_factory.build.return_value = {"node_name": "pve-hostA", "vm_id": 301}
    args_factory.resource_name_for.return_value = "lxc-1-app-1"

    fake_provider = object()
    provider_ctor = Mock(return_value=fake_provider)
    created_resource = object()
    container_ctor = Mock(return_value=created_resource)
    monkeypatch.setattr(
        deployment_module,
        "proxmoxve",
        SimpleNamespace(
            ct=SimpleNamespace(Container=container_ctor),
            Provider=provider_ctor,
        ),
    )

    mock_resource_options = Mock()
    monkeypatch.setattr(
        deployment_module.pulumi, "ResourceOptions", mock_resource_options
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

    # No nextid allocation needed (vm_id is explicit).
    nextid_client_cls.assert_not_called()
    vm_allocator_cls.assert_not_called()

    # Provider created once per host.
    provider_ctor.assert_called_once()
    _, prov_kw = provider_ctor.call_args
    assert prov_kw["endpoint"] == connection.endpoint

    # Container created with provider via ResourceOptions.
    container_ctor.assert_called_once()
    _, ct_kw = container_ctor.call_args
    assert ct_kw["node_name"] == "pve-hostA"
    mock_resource_options.assert_called_once_with(provider=fake_provider)

    export_map = dict(exports)
    assert export_map["yaml_file"] == "containers.yaml"
    assert export_map["container_count"] == 1
    assert export_map["container_names"] == ["app-1"]
    assert export_map["container_vm_ids"] == {"app-1": 301}
    assert export_map["container_hosts"] == {"app-1": "hostA"}


def test_run_allocates_vm_ids_per_host(monkeypatch) -> None:
    host_a = _host("hostA", "10.0.0.11")
    host_b = _host("hostB", "10.0.0.12")
    spec = DeploymentSpec(
        hosts={"hostA": host_a, "hostB": host_b},
        containers=[
            _container("app-1", "hostA", vm_id=None),
            _container("db-1", "hostB", vm_id=None),
        ],
    )
    conn_a = SimpleNamespace(
        endpoint="https://10.0.0.11:8006",
        insecure=False,
        api_token="TOKEN_A",
        username=None,
        password=None,
    )
    conn_b = SimpleNamespace(
        endpoint="https://10.0.0.12:8006",
        insecure=True,
        api_token="TOKEN_B",
        username=None,
        password=None,
    )

    config_reader = Mock()
    spec_loader = Mock()
    spec_service = Mock()
    args_factory = Mock()

    config_reader.get_containers_file.return_value = "containers.yaml"
    config_reader.get_host_connection_config.side_effect = (
        lambda alias, host: conn_a if alias == "hostA" else conn_b
    )
    spec_loader.load.return_value = {}
    spec_service.to_deployment_spec.return_value = spec
    args_factory.build.side_effect = (
        lambda container, host: {"node_name": host.node_name, "vm_id": container.vm_id}
    )
    args_factory.resource_name_for.side_effect = (
        lambda index, container_name: f"lxc-{index}-{container_name}"
    )

    allocate_calls = []

    class FakeNextIdClient:
        def __init__(self, cfg):
            pass

    class FakeAllocator:
        def __init__(self, client):
            pass

        def allocate_for_host(self, deployment_spec, host_alias):
            allocate_calls.append(host_alias)
            for c in deployment_spec.containers_for_host(host_alias):
                if c.vm_id is None:
                    c.vm_id = 500

    provider_ctor = Mock(return_value=object())
    container_ctor = Mock(return_value=object())
    monkeypatch.setattr(
        deployment_module,
        "proxmoxve",
        SimpleNamespace(
            ct=SimpleNamespace(Container=container_ctor),
            Provider=provider_ctor,
        ),
    )
    monkeypatch.setattr(deployment_module.pulumi, "ResourceOptions", Mock())
    monkeypatch.setattr(
        deployment_module.pulumi, "export", lambda k, v: None
    )
    monkeypatch.setattr(deployment_module, "ProxmoxNextIdClient", FakeNextIdClient)
    monkeypatch.setattr(deployment_module, "VmIdAllocator", FakeAllocator)

    service = DeploymentService(
        config_reader=config_reader,
        spec_loader=spec_loader,
        spec_service=spec_service,
        args_factory=args_factory,
    )
    service.run()

    # Both hosts should have had allocation called.
    assert sorted(allocate_calls) == ["hostA", "hostB"]
    # Provider per host.
    assert provider_ctor.call_count == 2
    # Container per container.
    assert container_ctor.call_count == 2

