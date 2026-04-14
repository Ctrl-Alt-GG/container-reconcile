from __future__ import annotations

from dataclasses import dataclass

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
    api_token: str | None
    username: str | None
    password: str | None
    otp: str | None
    auth_ticket: str | None
    csrf_prevention_token: str | None


@dataclass(slots=True)
class ContainerSpec:
    name: str
    host: str
    template_file_id: str
    vm_id: int | None
    unprivileged: bool
    ip: str
    gateway: str | None
    cores: int
    memory_mb: int
    disk_size_gb: int
    os_type: str
    hostname: str


@dataclass(slots=True)
class DeploymentSpec:
    hosts: dict[str, HostSpec]
    containers: list[ContainerSpec]

    def hosts_with_missing_vm_ids(self) -> set[str]:
        """Return host aliases that have at least one container without a vm_id."""
        return {c.host for c in self.containers if c.vm_id is None}

    def containers_for_host(self, alias: str) -> list[ContainerSpec]:
        return [c for c in self.containers if c.host == alias]

