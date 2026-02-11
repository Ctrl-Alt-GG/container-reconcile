from __future__ import annotations

from container_reconcile.domain.models import DeploymentSpec
from container_reconcile.infrastructure.proxmox_nextid_client import ProxmoxNextIdClient


class VmIdAllocator:
    """Allocates missing VM IDs using Proxmox next-id."""

    def __init__(self, next_id_client: ProxmoxNextIdClient) -> None:
        self._next_id_client = next_id_client

    def allocate(self, spec: DeploymentSpec) -> None:
        missing_indexes = [
            i for i, container in enumerate(spec.containers) if container.vm_id is None
        ]
        if not missing_indexes:
            return

        explicit_vm_ids = {
            container.vm_id for container in spec.containers if container.vm_id is not None
        }
        candidate = self._next_id_client.get_next_id()

        for idx in missing_indexes:
            while candidate in explicit_vm_ids:
                candidate += 1
            spec.containers[idx].vm_id = candidate
            explicit_vm_ids.add(candidate)
            candidate += 1

