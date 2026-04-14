from __future__ import annotations

import pulumi

from container_reconcile.domain.models import HostSpec, ProxmoxConnectionConfig


class ConfigReader:
    """Reads application and provider Pulumi configuration."""

    def __init__(self) -> None:
        self._app_cfg = pulumi.Config()
        self._provider_cfg = pulumi.Config("proxmoxve")

    def get_containers_file(self) -> str:
        return self._app_cfg.get("containersFile") or "containers.yaml"

    def get_host_connection_config(
        self, alias: str, host: HostSpec
    ) -> ProxmoxConnectionConfig:
        """Build connection config for a specific host.

        Per-host credentials are looked up first (e.g. ``<alias>.apiToken``),
        then global app-level keys (``proxmoxApiToken``), and finally the
        ``proxmoxve`` provider config (``apiToken`` / ``api_token``).
        """
        api_token = self._first_non_empty(
            self._app_cfg.get(f"{alias}.apiToken"),
            self._app_cfg.get("proxmoxApiToken"),
            self._provider_cfg.get("apiToken"),
            self._provider_cfg.get("api_token"),
        )
        username = self._first_non_empty(
            self._app_cfg.get(f"{alias}.username"),
            self._app_cfg.get("proxmoxUsername"),
            self._provider_cfg.get("username"),
        )
        password = self._first_non_empty(
            self._app_cfg.get(f"{alias}.password"),
            self._app_cfg.get("proxmoxPassword"),
            self._provider_cfg.get("password"),
        )
        otp = self._first_non_empty(
            self._app_cfg.get(f"{alias}.otp"),
            self._app_cfg.get("proxmoxOtp"),
            self._provider_cfg.get("otp"),
        )
        auth_ticket = self._first_non_empty(
            self._app_cfg.get(f"{alias}.authTicket"),
            self._app_cfg.get("proxmoxAuthTicket"),
            self._provider_cfg.get("authTicket"),
            self._provider_cfg.get("auth_ticket"),
        )
        csrf_prevention_token = self._first_non_empty(
            self._app_cfg.get(f"{alias}.csrfToken"),
            self._app_cfg.get("proxmoxCsrfToken"),
            self._provider_cfg.get("csrfPreventionToken"),
            self._provider_cfg.get("csrf_prevention_token"),
        )

        return ProxmoxConnectionConfig(
            endpoint=host.endpoint,
            insecure=host.insecure,
            api_token=api_token,
            username=username,
            password=password,
            otp=otp,
            auth_ticket=auth_ticket,
            csrf_prevention_token=csrf_prevention_token,
        )

    @staticmethod
    def _first_non_empty(*values: str | None) -> str | None:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value
        return None

