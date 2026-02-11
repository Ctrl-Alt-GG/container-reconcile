from __future__ import annotations

from unittest.mock import Mock

from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec
from container_reconcile.services.vm_id_allocator import VmIdAllocator


def test_allocate_is_noop_when_no_missing_vm_ids() -> None:
    host = HostSpec(
        alias="hostA",
        ip="10.0.0.11",
        node_name="node-a",
        datastore_id="local-lvm",
        bridge="vmbr0",
    )
    spec = DeploymentSpec(
        hosts={"hostA": host},
        containers=[
            ContainerSpec(
                name="app-1",
                host="hostA",
                template_file_id="local:vztmpl/ubuntu.tar.zst",
                vm_id=200,
                unprivileged=True,
                ip="dhcp",
                gateway=None,
                cores=1,
                memory_mb=512,
                disk_size_gb=8,
                os_type="ubuntu",
                hostname="app-1",
            )
        ],
    )
    next_id_client = Mock()
    allocator = VmIdAllocator(next_id_client)

    allocator.allocate(spec)

    next_id_client.get_next_id.assert_not_called()
    assert spec.containers[0].vm_id == 200


def test_allocate_assigns_sequential_ids_and_skips_collisions(
    sample_deployment_spec: DeploymentSpec,
) -> None:
    next_id_client = Mock()
    next_id_client.get_next_id.return_value = 201  # collides with explicit ID
    allocator = VmIdAllocator(next_id_client)

    # Add one more missing container to validate sequential allocation.
    sample_deployment_spec.containers.append(
        ContainerSpec(
            name="app-3",
            host="hostA",
            template_file_id="local:vztmpl/ubuntu.tar.zst",
            vm_id=None,
            unprivileged=True,
            ip="dhcp",
            gateway=None,
            cores=1,
            memory_mb=512,
            disk_size_gb=8,
            os_type="ubuntu",
            hostname="app-3",
        )
    )

    allocator.allocate(sample_deployment_spec)

    next_id_client.get_next_id.assert_called_once()
    vm_ids = {container.name: container.vm_id for container in sample_deployment_spec.containers}
    assert vm_ids["app-1"] == 201
    assert vm_ids["app-2"] == 202
    assert vm_ids["app-3"] == 203

