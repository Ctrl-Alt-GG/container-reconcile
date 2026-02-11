from __future__ import annotations

from typing import Optional

import requests

from container_reconcile.domain.errors import SpecError
from container_reconcile.infrastructure.config_reader import ProxmoxConnectionConfig


class ProxmoxNextIdClient:
    """Client for Proxmox /cluster/nextid resolution."""

    def __init__(self, connection: ProxmoxConnectionConfig) -> None:
        self._api_base = self._normalize_api_base(connection.endpoint)
        self._session = requests.Session()
        self._session.verify = not connection.insecure
        self._session.headers.update({"Accept": "application/json"})

        if connection.api_token:
            self._session.headers["Authorization"] = (
                f"PVEAPIToken={connection.api_token}"
            )
            return

        if connection.auth_ticket:
            self._session.cookies.set("PVEAuthCookie", connection.auth_ticket)
            if connection.csrf_prevention_token:
                self._session.headers["CSRFPreventionToken"] = (
                    connection.csrf_prevention_token
                )
            return

        if connection.username and connection.password:
            self._login(
                username=connection.username,
                password=connection.password,
                otp=connection.otp,
            )
            return

        raise SpecError(
            "Unable to authenticate for vm_id auto-allocation. Configure one of:\n"
            "- proxmoxve:apiToken\n"
            "- proxmoxve:username + proxmoxve:password\n"
            "- proxmoxve:authTicket (and optional proxmoxve:csrfPreventionToken)\n"
            "You can also override with container-reconcile config keys: "
            "proxmoxApiToken/proxmoxUsername/proxmoxPassword/proxmoxAuthTicket."
        )

    @staticmethod
    def _normalize_api_base(endpoint: str) -> str:
        stripped = endpoint.rstrip("/")
        if stripped.endswith("/api2/json"):
            return stripped
        return f"{stripped}/api2/json"

    def _login(self, username: str, password: str, otp: Optional[str]) -> None:
        login_url = f"{self._api_base}/access/ticket"
        payload = {"username": username, "password": password}
        if otp:
            payload["otp"] = otp

        try:
            response = self._session.post(login_url, data=payload, timeout=20)
            response.raise_for_status()
            login_data = response.json().get("data") or {}
        except requests.RequestException as exc:
            raise SpecError(
                f"Failed to authenticate to Proxmox API at '{self._api_base}'. {exc}"
            ) from exc

        ticket = login_data.get("ticket")
        if not ticket:
            raise SpecError("Proxmox login succeeded but no ticket was returned.")

        self._session.cookies.set("PVEAuthCookie", ticket)
        csrf = login_data.get("CSRFPreventionToken")
        if csrf:
            self._session.headers["CSRFPreventionToken"] = csrf

    def get_next_id(self) -> int:
        next_id_url = f"{self._api_base}/cluster/nextid"
        try:
            response = self._session.get(next_id_url, timeout=20)
            response.raise_for_status()
            data = response.json().get("data")
        except requests.RequestException as exc:
            raise SpecError(
                f"Failed to query Proxmox next-id at '{next_id_url}'. "
                "Check endpoint/auth/TLS configuration."
            ) from exc

        if data is None:
            raise SpecError("Proxmox next-id API returned no data.")

        try:
            return int(data)
        except (TypeError, ValueError) as exc:
            raise SpecError(f"Unexpected next-id payload '{data}'.") from exc

