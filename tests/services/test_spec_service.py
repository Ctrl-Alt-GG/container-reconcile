from __future__ import annotations

import copy

import pytest

from container_reconcile.domain.errors import SpecError
from container_reconcile.services.spec_service import SpecService


def test_to_deployment_spec_normalizes_and_applies_defaults(
    sample_raw_spec,
) -> None:
    raw = copy.deepcopy(sample_raw_spec)
    raw["hosts"]["hostA"]["node_name"] = " pve-node-a "
    raw["containers"][1]["hostname"] = " app-2 "
    raw["containers"][1]["os_type"] = " ubuntu "

    spec = SpecService().to_deployment_spec(raw)

    assert list(spec.hosts.keys()) == ["hostA"]
    assert len(spec.containers) == 2
    assert spec.hosts["hostA"].node_name == "pve-node-a"
    assert spec.hosts["hostA"].endpoint == "https://10.0.0.11:8006"
    assert spec.hosts["hostA"].insecure is False

    first = spec.containers[0]
    assert first.name == "app-1"
    assert first.vm_id == 201
    assert first.unprivileged is True
    assert first.ip == "10.0.0.101/24"
    assert first.gateway == "10.0.0.1"

    second = spec.containers[1]
    assert second.name == "app-2"
    assert second.vm_id is None
    assert second.unprivileged is True
    assert second.ip == "dhcp"
    assert second.gateway is None
    assert second.cores == 2
    assert second.memory_mb == 2048
    assert second.disk_size_gb == 8
    assert second.hostname == "app-2"
    assert second.os_type == "ubuntu"


def test_to_deployment_spec_requires_non_empty_hosts_and_containers() -> None:
    service = SpecService()

    with pytest.raises(SpecError, match="Top-level key 'hosts' must be a non-empty mapping"):
        service.to_deployment_spec({"hosts": {}, "containers": [{}]})

    with pytest.raises(SpecError, match="Top-level key 'containers' must be a non-empty list"):
        service.to_deployment_spec({"hosts": {"h": {}}, "containers": []})


def test_to_deployment_spec_rejects_unknown_host_reference(sample_raw_spec) -> None:
    raw = copy.deepcopy(sample_raw_spec)
    raw["containers"][0]["host"] = "unknown-host"

    with pytest.raises(SpecError, match="must reference a defined host"):
        SpecService().to_deployment_spec(raw)


def test_to_deployment_spec_rejects_duplicate_name_and_vm_id(sample_raw_spec) -> None:
    service = SpecService()

    dup_name = copy.deepcopy(sample_raw_spec)
    dup_name["containers"][1]["name"] = "app-1"
    with pytest.raises(SpecError, match="Duplicate container name 'app-1'"):
        service.to_deployment_spec(dup_name)

    dup_vm_id = copy.deepcopy(sample_raw_spec)
    dup_vm_id["containers"][1]["vm_id"] = 201
    with pytest.raises(SpecError, match="Duplicate vm_id '201'"):
        service.to_deployment_spec(dup_vm_id)


def test_to_deployment_spec_rejects_gateway_when_ip_is_dhcp(sample_raw_spec) -> None:
    raw = copy.deepcopy(sample_raw_spec)
    raw["containers"][1]["gateway"] = "10.0.0.1"

    with pytest.raises(SpecError, match="gateway cannot be set"):
        SpecService().to_deployment_spec(raw)


def test_to_deployment_spec_rejects_invalid_numeric_fields(sample_raw_spec) -> None:
    raw = copy.deepcopy(sample_raw_spec)
    raw["containers"][0]["cores"] = 0

    with pytest.raises(SpecError, match="must be a positive integer"):
        SpecService().to_deployment_spec(raw)


def test_to_deployment_spec_allows_same_vm_id_on_different_hosts() -> None:
    """Independent hosts have independent ID pools."""
    raw = {
        "hosts": {
            "hostA": {
                "ip": "10.0.0.11",
                "node_name": "pve-a",
                "datastore_id": "local-lvm",
                "bridge": "vmbr0",
            },
            "hostB": {
                "ip": "10.0.0.12",
                "node_name": "pve-b",
                "datastore_id": "local-lvm",
                "bridge": "vmbr0",
            },
        },
        "containers": [
            {
                "name": "app-1",
                "host": "hostA",
                "template_file_id": "local:vztmpl/ubuntu.tar.zst",
                "vm_id": 200,
            },
            {
                "name": "db-1",
                "host": "hostB",
                "template_file_id": "local:vztmpl/ubuntu.tar.zst",
                "vm_id": 200,  # same vm_id, different host -> OK
            },
        ],
    }
    spec = SpecService().to_deployment_spec(raw)
    assert spec.containers[0].vm_id == 200
    assert spec.containers[1].vm_id == 200


def test_to_deployment_spec_parses_host_endpoint_and_insecure() -> None:
    raw = {
        "hosts": {
            "h1": {
                "ip": "10.0.0.11",
                "node_name": "pve",
                "datastore_id": "local-lvm",
                "bridge": "vmbr0",
                "endpoint": "https://custom:443",
                "insecure": True,
            },
        },
        "containers": [
            {
                "name": "c1",
                "host": "h1",
                "template_file_id": "local:vztmpl/ubuntu.tar.zst",
            },
        ],
    }
    spec = SpecService().to_deployment_spec(raw)
    assert spec.hosts["h1"].endpoint == "https://custom:443"
    assert spec.hosts["h1"].insecure is True

