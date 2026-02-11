from __future__ import annotations

import re
from typing import Any, Dict

import pulumi_proxmoxve as proxmoxve

from container_reconcile.domain.models import ContainerSpec, HostSpec


class ContainerArgsFactory:
    """Builds Pulumi proxmoxve container args from domain specs."""

    def build(self, container: ContainerSpec, host: HostSpec) -> Dict[str, Any]:
        ipv4 = proxmoxve.ct.ContainerInitializationIpConfigIpv4Args(
            address=container.ip,
            gateway=container.gateway,
        )
        ip_config = proxmoxve.ct.ContainerInitializationIpConfigArgs(ipv4=ipv4)

        return {
            "node_name": host.node_name,
            "vm_id": container.vm_id,
            "unprivileged": container.unprivileged,
            "cpu": proxmoxve.ct.ContainerCpuArgs(
                cores=container.cores,
            ),
            "memory": proxmoxve.ct.ContainerMemoryArgs(
                dedicated=container.memory_mb,
            ),
            "disk": proxmoxve.ct.ContainerDiskArgs(
                datastore_id=host.datastore_id,
                size=container.disk_size_gb,
            ),
            "network_interfaces": [
                proxmoxve.ct.ContainerNetworkInterfaceArgs(
                    name="eth0",
                    bridge=host.bridge,
                )
            ],
            "initialization": proxmoxve.ct.ContainerInitializationArgs(
                hostname=container.hostname,
                ip_configs=[ip_config],
            ),
            "operating_system": proxmoxve.ct.ContainerOperatingSystemArgs(
                template_file_id=container.template_file_id,
                type=container.os_type,
            ),
        }

    def resource_name_for(self, index: int, container_name: str) -> str:
        return f"lxc-{index}-{self._sanitize_resource_name(container_name)}"

    @staticmethod
    def _sanitize_resource_name(name: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\-_]", "-", name).strip("-")
        return cleaned or "container"

