from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pulumi

from container_reconcile.domain.errors import SpecError


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


class ConfigReader:
    """Reads application and provider Pulumi configuration."""

    def __init__(self) -> None:
        self._app_cfg = pulumi.Config()
        self._provider_cfg = pulumi.Config("proxmoxve")

    def get_containers_file(self) -> str:
        return self._app_cfg.get("containersFile") or "containers.yaml"

    def get_proxmox_connection_config(self) -> ProxmoxConnectionConfig:
        endpoint = self._first_non_empty(
            self._app_cfg.get("proxmoxEndpoint"),
            self._provider_cfg.get("endpoint"),
        )
        if not endpoint:
            raise SpecError(
                "Proxmox endpoint is required for vm_id auto-allocation. "
                "Set 'proxmoxve:endpoint' (or 'container-reconcile:proxmoxEndpoint')."
            )

        insecure = self._first_non_none_bool(
            self._app_cfg.get_bool("proxmoxInsecure"),
            self._provider_cfg.get_bool("insecure"),
            False,
        )

        api_token = self._first_non_empty(
            self._app_cfg.get("proxmoxApiToken"),
            self._provider_cfg.get("apiToken"),
            self._provider_cfg.get("api_token"),
        )
        username = self._first_non_empty(
            self._app_cfg.get("proxmoxUsername"),
            self._provider_cfg.get("username"),
        )
        password = self._first_non_empty(
            self._app_cfg.get("proxmoxPassword"),
            self._provider_cfg.get("password"),
        )
        otp = self._first_non_empty(
            self._app_cfg.get("proxmoxOtp"),
            self._provider_cfg.get("otp"),
        )
        auth_ticket = self._first_non_empty(
            self._app_cfg.get("proxmoxAuthTicket"),
            self._provider_cfg.get("authTicket"),
            self._provider_cfg.get("auth_ticket"),
        )
        csrf_prevention_token = self._first_non_empty(
            self._app_cfg.get("proxmoxCsrfToken"),
            self._provider_cfg.get("csrfPreventionToken"),
            self._provider_cfg.get("csrf_prevention_token"),
        )

        return ProxmoxConnectionConfig(
            endpoint=endpoint,
            insecure=insecure,
            api_token=api_token,
            username=username,
            password=password,
            otp=otp,
            auth_ticket=auth_ticket,
            csrf_prevention_token=csrf_prevention_token,
        )

    @staticmethod
    def _first_non_empty(*values: Optional[str]) -> Optional[str]:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value
        return None

    @staticmethod
    def _first_non_none_bool(*values: Optional[bool]) -> bool:
        for value in values:
            if value is not None:
                return bool(value)
        return False

