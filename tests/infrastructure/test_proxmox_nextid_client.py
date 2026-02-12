from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import Mock

import pytest
import requests

import container_reconcile.infrastructure.proxmox_nextid_client as client_module
from container_reconcile.domain.errors import SpecError
from container_reconcile.domain.models import ProxmoxConnectionConfig
from container_reconcile.infrastructure.proxmox_nextid_client import ProxmoxNextIdClient


class _FakeResponse:
    def __init__(self, data: Any = None, raise_exc: Exception | None = None) -> None:
        self._data = data
        self._raise_exc = raise_exc

    def raise_for_status(self) -> None:
        if self._raise_exc:
            raise self._raise_exc

    def json(self) -> Dict[str, Any]:
        return {"data": self._data}


class _FakeCookies:
    def __init__(self) -> None:
        self.values: Dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.values[key] = value


class _FakeSession:
    def __init__(self) -> None:
        self.verify = True
        self.headers: Dict[str, str] = {}
        self.cookies = _FakeCookies()
        self.post = Mock()
        self.get = Mock()


def _connection(
    *,
    endpoint: str = "https://pve.example:8006",
    insecure: bool = False,
    api_token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    otp: Optional[str] = None,
    auth_ticket: Optional[str] = None,
    csrf_prevention_token: Optional[str] = None,
) -> ProxmoxConnectionConfig:
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


def test_init_with_api_token_sets_authorization_header(monkeypatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    ProxmoxNextIdClient(_connection(api_token="user@pam!token=secret"))

    assert session.verify is True
    assert session.headers["Authorization"] == "PVEAPIToken=user@pam!token=secret"
    assert session.headers["Accept"] == "application/json"


def test_init_with_auth_ticket_sets_cookie_and_csrf(monkeypatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    ProxmoxNextIdClient(
        _connection(auth_ticket="ticket-value", csrf_prevention_token="csrf-value")
    )

    assert session.cookies.values["PVEAuthCookie"] == "ticket-value"
    assert session.headers["CSRFPreventionToken"] == "csrf-value"


def test_init_with_username_password_performs_login(monkeypatch) -> None:
    session = _FakeSession()
    session.post.return_value = _FakeResponse(
        data={"ticket": "t-123", "CSRFPreventionToken": "csrf-123"}
    )
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    client = ProxmoxNextIdClient(
        _connection(username="root@pam", password="secret", otp="111222")
    )

    session.post.assert_called_once()
    post_args, post_kwargs = session.post.call_args
    assert post_args[0].endswith("/api2/json/access/ticket")
    assert post_kwargs["data"] == {
        "username": "root@pam",
        "password": "secret",
        "otp": "111222",
    }
    assert session.cookies.values["PVEAuthCookie"] == "t-123"
    assert session.headers["CSRFPreventionToken"] == "csrf-123"
    assert isinstance(client, ProxmoxNextIdClient)


def test_init_raises_when_no_auth_method_is_available(monkeypatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    with pytest.raises(SpecError, match="Unable to authenticate"):
        ProxmoxNextIdClient(_connection())


def test_get_next_id_returns_integer(monkeypatch) -> None:
    session = _FakeSession()
    session.get.return_value = _FakeResponse(data="321")
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    client = ProxmoxNextIdClient(_connection(api_token="token"))
    assert client.get_next_id() == 321


def test_get_next_id_raises_when_request_fails(monkeypatch) -> None:
    session = _FakeSession()
    session.get.return_value = _FakeResponse(
        data=None,
        raise_exc=requests.RequestException("network error"),
    )
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    client = ProxmoxNextIdClient(_connection(api_token="token"))
    with pytest.raises(SpecError, match="Failed to query Proxmox next-id"):
        client.get_next_id()


def test_get_next_id_raises_for_non_integer_payload(monkeypatch) -> None:
    session = _FakeSession()
    session.get.return_value = _FakeResponse(data={"bad": "value"})
    monkeypatch.setattr(client_module.requests, "Session", lambda: session)

    client = ProxmoxNextIdClient(_connection(api_token="token"))
    with pytest.raises(SpecError, match="Unexpected next-id payload"):
        client.get_next_id()

