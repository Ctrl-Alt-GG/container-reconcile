from __future__ import annotations

from typing import Any

from container_reconcile.domain.errors import SpecError
from container_reconcile.domain.models import (
    REQUIRED_CONTAINER_FIELDS,
    REQUIRED_HOST_FIELDS,
    ContainerSpec,
    DeploymentSpec,
    HostSpec,
)
from container_reconcile.domain.validators import FieldValidators

_DEFAULT_PROXMOX_PORT = 8006


class SpecService:
    """Validates and normalizes the raw YAML spec into typed domain models."""

    def to_deployment_spec(self, raw_spec: dict[str, Any]) -> DeploymentSpec:
        hosts_obj = raw_spec.get("hosts")
        containers_obj = raw_spec.get("containers")

        if not isinstance(hosts_obj, dict) or not hosts_obj:
            raise SpecError("Top-level key 'hosts' must be a non-empty mapping.")
        if not isinstance(containers_obj, list) or not containers_obj:
            raise SpecError("Top-level key 'containers' must be a non-empty list.")

        hosts: dict[str, HostSpec] = self._normalize_hosts(hosts_obj)
        containers: list[ContainerSpec] = self._normalize_containers(
            containers_obj=containers_obj,
            hosts=hosts,
        )
        return DeploymentSpec(hosts=hosts, containers=containers)

    def _normalize_hosts(self, hosts_obj: dict[str, Any]) -> dict[str, HostSpec]:
        normalized_hosts: dict[str, HostSpec] = {}
        for host_name, host_value in hosts_obj.items():
            if not isinstance(host_name, str) or not host_name.strip():
                raise SpecError("Every host key in 'hosts' must be a non-empty string.")
            if not isinstance(host_value, dict):
                raise SpecError(f"Host '{host_name}' must be an object.")

            for field in REQUIRED_HOST_FIELDS:
                if field not in host_value:
                    raise SpecError(
                        f"Host '{host_name}' is missing required field '{field}'."
                    )

            host_ip = host_value["ip"]
            if not isinstance(host_ip, str):
                raise SpecError(f"Host '{host_name}' field 'ip' must be a string.")
            FieldValidators.assert_ip(host_ip, f"hosts.{host_name}.ip")

            ctx = f"hosts.{host_name}"
            node_name = FieldValidators.assert_non_empty_string(
                host_value["node_name"], f"{ctx}.node_name"
            )
            datastore_id = FieldValidators.assert_non_empty_string(
                host_value["datastore_id"], f"{ctx}.datastore_id"
            )
            bridge = FieldValidators.assert_non_empty_string(
                host_value["bridge"], f"{ctx}.bridge"
            )

            raw_endpoint = host_value.get("endpoint")
            if raw_endpoint is not None:
                endpoint = FieldValidators.assert_non_empty_string(
                    raw_endpoint, f"{ctx}.endpoint"
                )
            else:
                endpoint = f"https://{host_ip}:{_DEFAULT_PROXMOX_PORT}"

            insecure = host_value.get("insecure", False)
            if not isinstance(insecure, bool):
                raise SpecError(f"Host '{host_name}' field 'insecure' must be a boolean.")

            normalized_hosts[host_name] = HostSpec(
                alias=host_name,
                ip=host_ip,
                node_name=node_name,
                datastore_id=datastore_id,
                bridge=bridge,
                endpoint=endpoint,
                insecure=insecure,
            )

        return normalized_hosts

    def _normalize_containers(
        self,
        containers_obj: list[Any],
        hosts: dict[str, HostSpec],
    ) -> list[ContainerSpec]:
        seen_container_names: set[str] = set()
        seen_vm_ids_per_host: dict[str, set[int]] = {alias: set() for alias in hosts}
        normalized_containers: list[ContainerSpec] = []

        for index, container_value in enumerate(containers_obj):
            context = f"containers[{index}]"
            if not isinstance(container_value, dict):
                raise SpecError(f"{context} must be an object.")

            for field in REQUIRED_CONTAINER_FIELDS:
                if field not in container_value:
                    raise SpecError(f"{context} is missing required field '{field}'.")

            name = FieldValidators.assert_non_empty_string(
                container_value["name"], f"{context}.name"
            )
            host_ref = container_value["host"]
            if not isinstance(host_ref, str) or host_ref not in hosts:
                raise SpecError(
                    f"{context}.host must reference a defined host in 'hosts'. Got '{host_ref}'."
                )

            template_file_id = FieldValidators.assert_non_empty_string(
                container_value["template_file_id"], f"{context}.template_file_id"
            )

            if name in seen_container_names:
                raise SpecError(f"Duplicate container name '{name}'.")
            seen_container_names.add(name)

            vm_id = self._normalize_vm_id(
                container_value, context, seen_vm_ids_per_host[host_ref]
            )

            unprivileged = container_value.get("unprivileged", True)
            if not isinstance(unprivileged, bool):
                raise SpecError(f"{context}.unprivileged must be a boolean when provided.")

            ip_value = container_value.get("ip", "dhcp")
            if not isinstance(ip_value, str):
                raise SpecError(f"{context}.ip must be a string when provided.")
            FieldValidators.assert_cidr_or_dhcp(ip_value, f"{context}.ip")

            gateway = container_value.get("gateway")
            if gateway is not None:
                if not isinstance(gateway, str):
                    raise SpecError(f"{context}.gateway must be a string when provided.")
                FieldValidators.assert_ip(gateway, f"{context}.gateway")
            if ip_value.lower() == "dhcp" and gateway is not None:
                raise SpecError(
                    f"{context}.gateway cannot be set when {context}.ip is 'dhcp'."
                )

            cores = FieldValidators.assert_positive_int(
                container_value.get("cores", 2),
                f"{context}.cores",
            )
            memory_mb = FieldValidators.assert_positive_int(
                container_value.get("memory_mb", 2048),
                f"{context}.memory_mb",
            )
            disk_size_gb = FieldValidators.assert_positive_int(
                container_value.get("disk_size_gb", 8),
                f"{context}.disk_size_gb",
            )

            os_type = FieldValidators.assert_non_empty_string(
                container_value.get("os_type", "ubuntu"), f"{context}.os_type"
            )

            hostname = FieldValidators.assert_non_empty_string(
                container_value.get("hostname", name), f"{context}.hostname"
            )

            normalized_containers.append(
                ContainerSpec(
                    name=name,
                    host=host_ref,
                    template_file_id=template_file_id,
                    vm_id=vm_id,
                    unprivileged=unprivileged,
                    ip=ip_value,
                    gateway=gateway,
                    cores=cores,
                    memory_mb=memory_mb,
                    disk_size_gb=disk_size_gb,
                    os_type=os_type,
                    hostname=hostname,
                )
            )

        return normalized_containers

    @staticmethod
    def _normalize_vm_id(
        container_value: dict[str, Any],
        context: str,
        seen_vm_ids: set[int],
    ) -> int | None:
        vm_id_value = container_value.get("vm_id")
        if vm_id_value is None:
            return None

        vm_id = FieldValidators.assert_positive_int(vm_id_value, f"{context}.vm_id")
        if vm_id in seen_vm_ids:
            raise SpecError(f"Duplicate vm_id '{vm_id}' in YAML.")
        seen_vm_ids.add(vm_id)
        return vm_id

