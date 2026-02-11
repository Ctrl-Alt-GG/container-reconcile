from __future__ import annotations

import pulumi_proxmoxve as proxmoxve

from container_reconcile.domain.models import ContainerSpec, HostSpec
from container_reconcile.services.container_args_factory import ContainerArgsFactory


def test_build_returns_typed_args_with_none_gateway(
    sample_host: HostSpec,
) -> None:
    container = ContainerSpec(
        name="app-1",
        host="hostA",
        template_file_id="local:vztmpl/ubuntu.tar.zst",
        vm_id=222,
        unprivileged=True,
        ip="dhcp",
        gateway=None,
        cores=2,
        memory_mb=1024,
        disk_size_gb=8,
        os_type="ubuntu",
        hostname="app-1",
    )
    factory = ContainerArgsFactory()

    args = factory.build(container=container, host=sample_host)

    assert args["node_name"] == sample_host.node_name
    assert args["vm_id"] == 222
    assert args["unprivileged"] is True

    assert isinstance(args["cpu"], proxmoxve.ct.ContainerCpuArgs)
    assert args["cpu"].cores == 2

    assert isinstance(args["memory"], proxmoxve.ct.ContainerMemoryArgs)
    assert args["memory"].dedicated == 1024

    assert isinstance(args["disk"], proxmoxve.ct.ContainerDiskArgs)
    assert args["disk"].datastore_id == sample_host.datastore_id

    assert isinstance(args["network_interfaces"][0], proxmoxve.ct.ContainerNetworkInterfaceArgs)
    assert args["network_interfaces"][0].bridge == sample_host.bridge

    assert isinstance(args["initialization"], proxmoxve.ct.ContainerInitializationArgs)
    assert args["initialization"].hostname == "app-1"

    ip_config = args["initialization"].ip_configs[0]
    assert isinstance(ip_config, proxmoxve.ct.ContainerInitializationIpConfigArgs)
    assert isinstance(ip_config.ipv4, proxmoxve.ct.ContainerInitializationIpConfigIpv4Args)
    assert ip_config.ipv4.address == "dhcp"
    assert ip_config.ipv4.gateway is None

    assert isinstance(args["operating_system"], proxmoxve.ct.ContainerOperatingSystemArgs)
    assert args["operating_system"].template_file_id == "local:vztmpl/ubuntu.tar.zst"
    assert args["operating_system"].type == "ubuntu"


def test_resource_name_for_sanitizes_name() -> None:
    factory = ContainerArgsFactory()
    assert factory.resource_name_for(1, "My App@Prod!") == "lxc-1-My-App-Prod"


def test_resource_name_for_falls_back_to_container_when_empty_after_sanitize() -> None:
    factory = ContainerArgsFactory()
    assert factory.resource_name_for(9, "!!!") == "lxc-9-container"

