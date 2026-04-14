from __future__ import annotations

import container_reconcile.infrastructure.config_reader as config_reader_module
from container_reconcile.domain.models import HostSpec
from container_reconcile.infrastructure.config_reader import ConfigReader


def _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg) -> None:
    def fake_config(namespace=None):
        if namespace == "proxmoxve":
            return provider_cfg
        return app_cfg

    monkeypatch.setattr(config_reader_module.pulumi, "Config", fake_config)


def _host(alias: str = "hostA") -> HostSpec:
    return HostSpec(
        alias=alias,
        ip="10.0.0.11",
        node_name="pve-node-a",
        datastore_id="local-lvm",
        bridge="vmbr0",
        endpoint="https://10.0.0.11:8006",
        insecure=False,
    )


def test_get_containers_file_uses_default_when_not_set(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={})
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    assert reader.get_containers_file() == "containers.yaml"


def test_get_containers_file_uses_app_override(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={"containersFile": "custom-containers.yaml"})
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    assert reader.get_containers_file() == "custom-containers.yaml"


def test_get_host_connection_config_uses_per_host_keys(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(
        values={
            "hostA.apiToken": "HOST_TOKEN",
            "hostA.username": "host-user",
            "hostA.password": "host-pass",
            "hostA.otp": "000111",
            "hostA.authTicket": "host-ticket",
            "hostA.csrfToken": "host-csrf",
            # Global keys should be ignored when per-host are set.
            "proxmoxApiToken": "GLOBAL_TOKEN",
        },
    )
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    host = _host("hostA")
    config = reader.get_host_connection_config("hostA", host)

    assert config.endpoint == "https://10.0.0.11:8006"
    assert config.insecure is False
    assert config.api_token == "HOST_TOKEN"
    assert config.username == "host-user"
    assert config.password == "host-pass"
    assert config.otp == "000111"
    assert config.auth_ticket == "host-ticket"
    assert config.csrf_prevention_token == "host-csrf"


def test_get_host_connection_config_falls_back_to_global_app_keys(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(
        values={
            "proxmoxApiToken": "APP_TOKEN",
            "proxmoxUsername": "app-user",
            "proxmoxPassword": "app-pass",
            "proxmoxOtp": "123456",
            "proxmoxAuthTicket": "app-ticket",
            "proxmoxCsrfToken": "app-csrf",
        },
    )
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    config = reader.get_host_connection_config("hostA", _host())

    assert config.api_token == "APP_TOKEN"
    assert config.username == "app-user"
    assert config.password == "app-pass"
    assert config.otp == "123456"
    assert config.auth_ticket == "app-ticket"
    assert config.csrf_prevention_token == "app-csrf"


def test_get_host_connection_config_falls_back_to_provider_keys(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={})
    provider_cfg = make_fake_config(
        values={
            "apiToken": "PROVIDER_TOKEN",
            "username": "provider-user",
            "password": "provider-pass",
            "otp": "654321",
            "auth_ticket": "provider-ticket",
            "csrf_prevention_token": "provider-csrf",
        },
    )
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    config = reader.get_host_connection_config("hostA", _host())

    assert config.api_token == "PROVIDER_TOKEN"
    assert config.username == "provider-user"
    assert config.password == "provider-pass"
    assert config.otp == "654321"
    assert config.auth_ticket == "provider-ticket"
    assert config.csrf_prevention_token == "provider-csrf"


def test_get_host_connection_config_takes_endpoint_and_insecure_from_host(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={})
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    host = HostSpec(
        alias="hostB",
        ip="10.0.0.12",
        node_name="pve-b",
        datastore_id="local-lvm",
        bridge="vmbr1",
        endpoint="https://custom.endpoint:443",
        insecure=True,
    )

    reader = ConfigReader()
    config = reader.get_host_connection_config("hostB", host)

    assert config.endpoint == "https://custom.endpoint:443"
    assert config.insecure is True

