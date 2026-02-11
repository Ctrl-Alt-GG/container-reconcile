from __future__ import annotations

import pytest

import container_reconcile.infrastructure.config_reader as config_reader_module
from container_reconcile.domain.errors import SpecError
from container_reconcile.infrastructure.config_reader import ConfigReader


def _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg) -> None:
    def fake_config(namespace=None):
        if namespace == "proxmoxve":
            return provider_cfg
        return app_cfg

    monkeypatch.setattr(config_reader_module.pulumi, "Config", fake_config)


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


def test_get_proxmox_connection_config_requires_endpoint(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={})
    provider_cfg = make_fake_config(values={})
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    with pytest.raises(SpecError, match="Proxmox endpoint is required"):
        reader.get_proxmox_connection_config()


def test_get_proxmox_connection_config_prefers_app_values(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(
        values={
            "proxmoxEndpoint": "https://app.example:8006",
            "proxmoxApiToken": "APP_TOKEN",
            "proxmoxUsername": "app-user",
            "proxmoxPassword": "app-pass",
            "proxmoxOtp": "123456",
            "proxmoxAuthTicket": "app-ticket",
            "proxmoxCsrfToken": "app-csrf",
        },
        bool_values={"proxmoxInsecure": True},
    )
    provider_cfg = make_fake_config(
        values={
            "endpoint": "https://provider.example:8006",
            "apiToken": "PROVIDER_TOKEN",
            "username": "provider-user",
            "password": "provider-pass",
        },
        bool_values={"insecure": False},
    )
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    config = reader.get_proxmox_connection_config()

    assert config.endpoint == "https://app.example:8006"
    assert config.insecure is True
    assert config.api_token == "APP_TOKEN"
    assert config.username == "app-user"
    assert config.password == "app-pass"
    assert config.otp == "123456"
    assert config.auth_ticket == "app-ticket"
    assert config.csrf_prevention_token == "app-csrf"


def test_get_proxmox_connection_config_falls_back_to_provider_snake_case(
    monkeypatch,
    make_fake_config,
) -> None:
    app_cfg = make_fake_config(values={})
    provider_cfg = make_fake_config(
        values={
            "endpoint": "https://provider.example:8006",
            "api_token": "PROVIDER_TOKEN",
            "auth_ticket": "provider-ticket",
            "csrf_prevention_token": "provider-csrf",
        },
        bool_values={"insecure": False},
    )
    _patch_pulumi_config(monkeypatch, app_cfg, provider_cfg)

    reader = ConfigReader()
    config = reader.get_proxmox_connection_config()

    assert config.endpoint == "https://provider.example:8006"
    assert config.insecure is False
    assert config.api_token == "PROVIDER_TOKEN"
    assert config.auth_ticket == "provider-ticket"
    assert config.csrf_prevention_token == "provider-csrf"

