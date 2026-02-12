from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


REQUIRED_HOST_FIELDS = ("ip", "node_name", "datastore_id", "bridge")
REQUIRED_CONTAINER_FIELDS = ("name", "host", "template_file_id")


@dataclass(slots=True)
class HostSpec:
    alias: str
    ip: str
    node_name: str
    datastore_id: str
    bridge: str
    endpoint: str
    insecure: bool


@dataclass(slots=True)
class ProxmoxConnectionConfig:
    endpoint: str
    insecure: bool
    api_token: Optional[str]
    username: Optional[str]
    password: Optional[str]
    otp: Optional[str]
    auth_ticket: Optional[str]
    csrf_prevention_token: Optional[str]


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

    def hosts_with_missing_vm_ids(self) -> Set[str]:
        """Return host aliases that have at least one container without a vm_id."""
        return {c.host for c in self.containers if c.vm_id is None}

    def containers_for_host(self, alias: str) -> List[ContainerSpec]:
        return [c for c in self.containers if c.host == alias]

