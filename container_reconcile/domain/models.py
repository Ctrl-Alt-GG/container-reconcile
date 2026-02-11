from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


REQUIRED_HOST_FIELDS = ("ip", "node_name", "datastore_id", "bridge")
REQUIRED_CONTAINER_FIELDS = ("name", "host", "template_file_id")


@dataclass(slots=True)
class HostSpec:
    alias: str
    ip: str
    node_name: str
    datastore_id: str
    bridge: str


@dataclass(slots=True)
class ContainerSpec:
    name: str
    host: str
    template_file_id: str
    vm_id: Optional[int]
    unprivileged: bool
    ip: str
    gateway: Optional[str]
    cores: int
    memory_mb: int
    disk_size_gb: int
    os_type: str
    hostname: str


@dataclass(slots=True)
class DeploymentSpec:
    hosts: Dict[str, HostSpec]
    containers: List[ContainerSpec]

    def has_missing_vm_ids(self) -> bool:
        return any(container.vm_id is None for container in self.containers)

