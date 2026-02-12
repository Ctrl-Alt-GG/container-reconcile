from __future__ import annotations

from typing import Dict, List

import pulumi
import pulumi_proxmoxve as proxmoxve

from container_reconcile.infrastructure.config_reader import ConfigReader
from container_reconcile.infrastructure.proxmox_nextid_client import ProxmoxNextIdClient
from container_reconcile.infrastructure.spec_loader import SpecLoader
from container_reconcile.services.container_args_factory import ContainerArgsFactory
from container_reconcile.services.spec_service import SpecService
from container_reconcile.services.vm_id_allocator import VmIdAllocator


class DeploymentService:
    """Coordinates parsing, allocation, deployment, and output export."""

    def __init__(
        self,
        config_reader: ConfigReader,
        spec_loader: SpecLoader,
        spec_service: SpecService,
        args_factory: ContainerArgsFactory,
    ) -> None:
        self._config_reader = config_reader
        self._spec_loader = spec_loader
        self._spec_service = spec_service
        self._args_factory = args_factory

    def run(self) -> None:
        yaml_path = self._config_reader.get_containers_file()
        raw_spec = self._spec_loader.load(yaml_path)
        deployment_spec = self._spec_service.to_deployment_spec(raw_spec)

        # --- Allocate missing vm_ids per host ---
        for host_alias in deployment_spec.hosts_with_missing_vm_ids():
            host = deployment_spec.hosts[host_alias]
            connection = self._config_reader.get_host_connection_config(
                host_alias, host
            )
            nextid_client = ProxmoxNextIdClient(connection)
            allocator = VmIdAllocator(nextid_client)
            allocator.allocate_for_host(deployment_spec, host_alias)

        # --- Create an explicit Pulumi provider per host ---
        providers: Dict[str, proxmoxve.Provider] = {}
        for alias, host in deployment_spec.hosts.items():
            connection = self._config_reader.get_host_connection_config(alias, host)
            providers[alias] = proxmoxve.Provider(
                f"proxmox-{alias}",
                endpoint=connection.endpoint,
                insecure=connection.insecure,
                api_token=connection.api_token,
                username=connection.username,
                password=connection.password,
            )

        # --- Deploy container resources ---
        created_resources: List[proxmoxve.ct.Container] = []
        vm_ids_by_name: Dict[str, int] = {}
        host_by_name: Dict[str, str] = {}

        for idx, container in enumerate(deployment_spec.containers):
            host = deployment_spec.hosts[container.host]
            container_args = self._args_factory.build(container=container, host=host)
            resource_name = self._args_factory.resource_name_for(
                index=idx + 1,
                container_name=container.name,
            )
            resource = proxmoxve.ct.Container(
                resource_name,
                **container_args,
                opts=pulumi.ResourceOptions(
                    provider=providers[container.host],
                ),
            )

            created_resources.append(resource)
            assert container.vm_id is not None
            vm_ids_by_name[container.name] = container.vm_id
            host_by_name[container.name] = container.host

        pulumi.export("yaml_file", yaml_path)
        pulumi.export("container_count", len(created_resources))
        pulumi.export(
            "container_names",
            [container.name for container in deployment_spec.containers],
        )
        pulumi.export("container_vm_ids", vm_ids_by_name)
        pulumi.export("container_hosts", host_by_name)

