from __future__ import annotations

import ipaddress
from typing import Any

from .errors import SpecError


class FieldValidators:
    @staticmethod
    def assert_ip(value: str, field_name: str) -> None:
        try:
            ipaddress.ip_address(value)
        except ValueError as exc:
            raise SpecError(f"Invalid IP address for '{field_name}': '{value}'.") from exc

    @staticmethod
    def assert_cidr_or_dhcp(value: str, field_name: str) -> None:
        if value.lower() == "dhcp":
            return
        try:
            ipaddress.ip_interface(value)
        except ValueError as exc:
            raise SpecError(
                f"Invalid CIDR address for '{field_name}': '{value}'. Expected like '10.0.0.10/24' or 'dhcp'."
            ) from exc

    @staticmethod
    def assert_positive_int(value: Any, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise SpecError(f"Field '{field_name}' must be a positive integer.")
        return value

    @staticmethod
    def assert_non_empty_string(value: Any, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise SpecError(f"Field '{field_name}' must be a non-empty string.")
        return value.strip()

