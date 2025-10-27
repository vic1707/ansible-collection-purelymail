from typing import Any
from unittest.mock import MagicMock

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import (
	RoutingRule,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	ListRoutingResponse,
)
from ansible_collections.bofzilla.purelymail.plugins.modules.crud import create_route
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import (
	AnsibleExitJson,
	bootstrap_module,
)

EXISTING_RULES = [
	RoutingRule(
		id=1,
		matchUser="toto",
		prefix=True,
		catchall=False,
		domainName="example.com",
		targetAddresses=["admin@example.com"],
	),
	RoutingRule(
		id=2,
		matchUser="admin",
		prefix=True,
		catchall=False,
		domainName="example.com",
		targetAddresses=["support@example.com"],
	),
]
NEW_RULE = RoutingRule(
	id=69,  # never used
	matchUser="",
	prefix=True,
	catchall=True,
	domainName="example.com",
	targetAddresses=["support@example.com"],
)
MOCKED_RESPONSE = ListRoutingResponse(EXISTING_RULES)


def run(
	monkeypatch: pytest.MonkeyPatch,
	rule_to_create: RoutingRule,
	*,
	diff: bool = False,
	check_mode: bool = False,
) -> tuple[Any, dict[str, MagicMock]]:
	mocks = bootstrap_module(monkeypatch, create_route, ("RoutingClient",))
	module = mocks["AnsibleModule"]
	routing_client = mocks["RoutingClient"]

	module._diff = diff
	module.check_mode = check_mode
	module.params = {
		"api_token": "dQw4w9WgXcQ",
		"domain_name": rule_to_create.domainName,
		"match_user": rule_to_create.matchUser,
		"target_addresses": rule_to_create.targetAddresses,
		"prefix": rule_to_create.prefix,
		"catchall": rule_to_create.catchall,
	}

	routing_client.list_routes.return_value = MOCKED_RESPONSE

	with pytest.raises(AnsibleExitJson) as excinfo:
		create_route.main()

	return excinfo.value.args[0], mocks


def test_diff_mode_successful_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, NEW_RULE, diff=True)
	mocks["RoutingClient"].create_route.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
			"after": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
				{ "prefix": True, "catchall": True, "domainName": "example.com", "matchUser": "", "targetAddresses": ["support@example.com"] },
			],
		},
	}


def test_diff_mode_nothing_to_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0], diff=True)
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
			"after": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
		},
	}


def test_check_mode(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, NEW_RULE, check_mode=True)
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0], check_mode=True)
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(
		monkeypatch,
		NEW_RULE,
		check_mode=True,
		diff=True,
	)
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
			"after": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
				{ "prefix": True, "catchall": True, "domainName": "example.com", "matchUser": "", "targetAddresses": ["support@example.com"] },
			],
		},
	}


def test_diff_and_check_modes_nothing_to_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0], check_mode=True, diff=True)
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
			"after": [
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"] },
				{ "prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"] },
			],
		},
	}


def test_normal_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, NEW_RULE)
	mocks["RoutingClient"].create_route.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_create(monkeypatch: pytest.MonkeyPatch):
	data, mocks = run(monkeypatch, EXISTING_RULES[0])
	mocks["RoutingClient"].create_route.assert_not_called()
	assert data == {"changed": False}
