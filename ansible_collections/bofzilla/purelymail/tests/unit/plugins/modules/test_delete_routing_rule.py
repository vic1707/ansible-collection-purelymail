import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.routing import delete_routing_rule
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_RULES = [
	RoutingRule(id=1, match_user="toto", prefix=True, catchall=False, domain_name="example.com", target_addresses=["admin@example.com"]),
	RoutingRule(id=2, match_user="admin", prefix=True, catchall=False, domain_name="example.com", target_addresses=["support@example.com"]),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		delete_routing_rule,
		(
			(
				"RoutingClient",
				lambda mock: setattr(mock.list_routing_rules, "return_value", ListRoutingResponse(EXISTING_RULES)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(rule_id: int, **kwargs):
		return runner_run(
			params={"routing_rule_id": rule_id},
			**kwargs,
		)

	return inner_run


def test_diff_mode_successful_delete(run):
	data, mocks = run(EXISTING_RULES[0].id, diff=True)

	mocks["RoutingClient"].delete_routing_rule.assert_called_once()
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


def test_diff_mode_nothing_to_delete(run):
	data, mocks = run(69, diff=True)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
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


def test_check_mode(run):
	data, mocks = run(EXISTING_RULES[0].id, check_mode=True)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_delete(run):
	data, mocks = run(69, check_mode=True)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(run):
	data, mocks = run(EXISTING_RULES[0].id, check_mode=True, diff=True)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
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


def test_diff_and_check_modes_nothing_to_delete(run):
	data, mocks = run(69, check_mode=True, diff=True)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
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


def test_normal_delete(run):
	data, mocks = run(EXISTING_RULES[0].id)

	mocks["RoutingClient"].delete_routing_rule.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_delete(run):
	data, mocks = run(69)

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}
