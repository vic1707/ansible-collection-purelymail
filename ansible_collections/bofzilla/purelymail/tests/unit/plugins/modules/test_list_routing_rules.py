from typing import Any
from unittest.mock import MagicMock

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.routing import list_routing_rules
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import AnsibleExitJson, bootstrap_module

EXISTING_RULES = [
	RoutingRule(id=1, matchUser="toto", prefix=True, catchall=False, domainName="example.com", targetAddresses=["admin@example.com"]),
	RoutingRule(id=2, matchUser="admin", prefix=True, catchall=False, domainName="example.com", targetAddresses=["support@example.com"]),
]


def run(
	monkeypatch: pytest.MonkeyPatch,
	*,
	diff: bool = False,
	check_mode: bool = False,
) -> tuple[Any, dict[str, MagicMock]]:
	mocks = bootstrap_module(monkeypatch, list_routing_rules, ("RoutingClient",))
	module = mocks["AnsibleModule"]
	routing_client = mocks["RoutingClient"]

	module._diff = diff
	module.check_mode = check_mode
	module.params = {"api_token": "dQw4w9WgXcQ"}

	routing_client.list_routing_rules.return_value = ListRoutingResponse(EXISTING_RULES)

	with pytest.raises(AnsibleExitJson) as excinfo:
		list_routing_rules.main()

	return excinfo.value.args[0], mocks


def test_diff(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, diff=True)
	assert data == {
		"changed": False,
		"rules": [
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
		],
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


def test_check(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, check_mode=True)
	assert data == {"changed": False}


def test_check_and_diff(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch, check_mode=True, diff=True)
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


def test_normal(monkeypatch: pytest.MonkeyPatch):
	data, _ = run(monkeypatch)
	assert data == {
		"changed": False,
		"rules": [
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
		],
	}
