from typing import Any
from unittest.mock import MagicMock

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import (
	RoutingRule,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	ListRoutingResponse,
)
from ansible_collections.bofzilla.purelymail.plugins.modules.crud import delete_route
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import (
	AnsibleExitJson,
	bootstrap_module,
)

EXISTING_RULES = [
	RoutingRule(id=1, matchUser="toto", prefix=True, catchall=False, domainName="example.com", targetAddresses=["admin@example.com"]),
	RoutingRule(id=2, matchUser="admin", prefix=True, catchall=False, domainName="example.com", targetAddresses=["support@example.com"]),
]


def run(
	monkeypatch: pytest.MonkeyPatch,
	id: int,
	*,
	diff: bool = False,
	check_mode: bool = False,
) -> tuple[Any, dict[str, MagicMock]]:
	mocks = bootstrap_module(monkeypatch, delete_route, ("RoutingClient",))
	module = mocks["AnsibleModule"]
	routing_client = mocks["RoutingClient"]

	module._diff = diff
	module.check_mode = check_mode
	module.params = {"api_token": "dQw4w9WgXcQ", "routing_rule_id": id}

	routing_client.list_routes.return_value = ListRoutingResponse(EXISTING_RULES)

	with pytest.raises(AnsibleExitJson) as excinfo:
		delete_route.main()

	return excinfo.value.args[0], mocks


def test_diff_mode_successful_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0].id, diff=True)
	mocks["RoutingClient"].delete_route.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2}
			],
		},
	}


def test_diff_mode_nothing_to_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, 69, diff=True)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
		},
	}


def test_check_mode(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0].id, check_mode=True)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, 69, check_mode=True)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0].id, check_mode=True, diff=True)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
		},
	}


def test_diff_and_check_modes_nothing_to_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, 69, check_mode=True, diff=True)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
			],
		},
	}


def test_normal_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0].id)
	mocks["RoutingClient"].delete_route.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_delete(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, 69)
	mocks["RoutingClient"].delete_route.assert_not_called()
	assert data == {"changed": False}
