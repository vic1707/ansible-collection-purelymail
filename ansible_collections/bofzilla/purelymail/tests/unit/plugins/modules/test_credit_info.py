from typing import Any
from unittest.mock import MagicMock

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	CheckCreditResponse,
)
from ansible_collections.bofzilla.purelymail.plugins.modules.crud import credit_info
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import (
	AnsibleExitJson,
	bootstrap_module,
)


def run(
	monkeypatch: pytest.MonkeyPatch,
	*,
	diff: bool = False,
	check_mode: bool = False,
) -> tuple[Any, dict[str, MagicMock]]:
	mocks = bootstrap_module(monkeypatch, credit_info, ("BillingClient",))
	module = mocks["AnsibleModule"]
	billing_client = mocks["BillingClient"]

	module._diff = diff
	module.check_mode = check_mode
	module.params = {"api_token": "dQw4w9WgXcQ"}

	billing_client.account_credit.return_value = CheckCreditResponse(credit="12.34")

	with pytest.raises(AnsibleExitJson) as excinfo:
		credit_info.main()

	return excinfo.value.args[0], mocks


def test_diff(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, diff=True)
	assert data == {
		"changed": False,
		"diff": {"before": {"credit": 12.34}, "after": {"credit": 12.34}},
	}


def test_check(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, check_mode=True)
	assert data == {"changed": False, "diff": None}


def test_check_and_diff(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, diff=True, check_mode=True)
	assert data == {
		"changed": False,
		"diff": {"before": {"credit": 12.34}, "after": {"credit": 12.34}},
	}


def test_normal(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch)
	assert data == {"changed": False, "credit": 12.34}
