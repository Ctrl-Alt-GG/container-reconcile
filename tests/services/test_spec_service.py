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

