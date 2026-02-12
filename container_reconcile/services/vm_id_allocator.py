from __future__ import annotations

from container_reconcile.domain.models import DeploymentSpec
from container_reconcile.infrastructure.proxmox_nextid_client import ProxmoxNextIdClient


class VmIdAllocator:
    """Allocates missing VM IDs for a single host using Proxmox next-id."""

    def __init__(self, next_id_client: ProxmoxNextIdClient) -> None:
        self._next_id_client = next_id_client

    def allocate_for_host(self, spec: DeploymentSpec, host_alias: str) -> None:
        """Fill in missing vm_ids for containers on *host_alias*."""
        host_indices = [
            i
            for i, c in enumerate(spec.containers)
            if c.host == host_alias
        ]
        missing_indices = [
            i for i in host_indices if spec.containers[i].vm_id is None
        ]
        if not missing_indices:
            return

        explicit_vm_ids = {
            spec.containers[i].vm_id
            for i in host_indices
            if spec.containers[i].vm_id is not None
        }
        candidate = self._next_id_client.get_next_id()

        for idx in missing_indices:
            while candidate in explicit_vm_ids:
                candidate += 1
            spec.containers[idx].vm_id = candidate
            explicit_vm_ids.add(candidate)
            candidate += 1

