from __future__ import annotations

from unittest.mock import Mock

from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec
from container_reconcile.services.vm_id_allocator import VmIdAllocator


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
    name: str,
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


def test_allocate_for_host_is_noop_when_no_missing_vm_ids() -> None:
    spec = DeploymentSpec(
        hosts={"hostA": _host()},
        containers=[_container("app-1", vm_id=200)],
    )
    next_id_client = Mock()
    allocator = VmIdAllocator(next_id_client)

    allocator.allocate_for_host(spec, "hostA")

    next_id_client.get_next_id.assert_not_called()
    assert spec.containers[0].vm_id == 200


def test_allocate_for_host_assigns_sequential_ids_and_skips_collisions() -> None:
    spec = DeploymentSpec(
        hosts={"hostA": _host()},
        containers=[
            _container("app-1", vm_id=201),
            _container("app-2", vm_id=None),
            _container("app-3", vm_id=None),
        ],
    )
    next_id_client = Mock()
    next_id_client.get_next_id.return_value = 201  # collides with explicit
    allocator = VmIdAllocator(next_id_client)

    allocator.allocate_for_host(spec, "hostA")

    next_id_client.get_next_id.assert_called_once()
    ids = {c.name: c.vm_id for c in spec.containers}
    assert ids["app-1"] == 201
    assert ids["app-2"] == 202
    assert ids["app-3"] == 203


def test_allocate_for_host_only_affects_target_host() -> None:
    """Containers on other hosts should not be touched."""
    spec = DeploymentSpec(
        hosts={"hostA": _host("hostA"), "hostB": _host("hostB", "10.0.0.12")},
        containers=[
            _container("app-1", host="hostA", vm_id=None),
            _container("db-1", host="hostB", vm_id=None),
        ],
    )
    next_id_client = Mock()
    next_id_client.get_next_id.return_value = 100
    allocator = VmIdAllocator(next_id_client)

    allocator.allocate_for_host(spec, "hostA")

    assert spec.containers[0].vm_id == 100  # hostA container allocated
    assert spec.containers[1].vm_id is None  # hostB untouched

