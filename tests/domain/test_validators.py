import pytest

from container_reconcile.domain.errors import SpecError
from container_reconcile.domain.validators import FieldValidators


def test_assert_ip_accepts_ipv4_and_ipv6() -> None:
    FieldValidators.assert_ip("10.0.0.1", "x.ip")
    FieldValidators.assert_ip("::1", "x.ip")


def test_assert_ip_rejects_invalid_value() -> None:
    with pytest.raises(SpecError, match="Invalid IP address"):
        FieldValidators.assert_ip("not-an-ip", "x.ip")


@pytest.mark.parametrize("value", ["dhcp", "DHCP", "10.0.0.10/24", "2001:db8::10/64"])
def test_assert_cidr_or_dhcp_accepts_valid_values(value: str) -> None:
    FieldValidators.assert_cidr_or_dhcp(value, "container.ip")


@pytest.mark.parametrize("value", ["10.0.0.10/", "bad-cidr", ""])
def test_assert_cidr_or_dhcp_rejects_invalid_values(value: str) -> None:
    with pytest.raises(SpecError, match="Invalid CIDR address"):
        FieldValidators.assert_cidr_or_dhcp(value, "container.ip")


def test_assert_positive_int_accepts_positive_integer() -> None:
    assert FieldValidators.assert_positive_int(7, "container.cores") == 7


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "1"])
def test_assert_positive_int_rejects_non_positive_or_non_integer(value: object) -> None:
    with pytest.raises(SpecError, match="must be a positive integer"):
        FieldValidators.assert_positive_int(value, "container.cores")


def test_assert_non_empty_string_trims_input() -> None:
    assert (
        FieldValidators.assert_non_empty_string("  my-value  ", "field")
        == "my-value"
    )


@pytest.mark.parametrize("value", [None, "", "   ", 42])
def test_assert_non_empty_string_rejects_invalid_values(value: object) -> None:
    with pytest.raises(SpecError, match="must be a non-empty string"):
        FieldValidators.assert_non_empty_string(value, "field")

