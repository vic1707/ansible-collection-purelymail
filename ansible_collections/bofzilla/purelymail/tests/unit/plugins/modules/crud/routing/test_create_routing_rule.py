import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.routing import create_routing_rule
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_RULES = [
	RoutingRule(id=1, match_user="toto", prefix=True, catchall=False, domain_name="example.com", target_addresses=["admin@example.com"]),
	RoutingRule(id=2, match_user="admin", prefix=True, catchall=False, domain_name="example.com", target_addresses=["support@example.com"]),
]
NEW_RULE = RoutingRule(
	id=99999,  # never used
	match_user="",
	prefix=True,
	catchall=True,
	domain_name="example.com",
	target_addresses=["support@example.com"],
)


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		create_routing_rule,
		(
			(
				"RoutingClient",
				lambda mock: setattr(mock.list_routing_rules, "return_value", ListRoutingResponse(EXISTING_RULES)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(rule: RoutingRule, **kwargs):
		params = {
			"domain_name": rule.domainName,
			"match_user": rule.matchUser,
			"target_addresses": rule.targetAddresses,
			"prefix": rule.prefix,
			"catchall": rule.catchall,
		}
		return runner_run(params=params, **kwargs)

	return inner_run


def test_diff_mode_successful_create(run):
	data, mocks = run(NEW_RULE, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
				{"prefix": True, "catchall": True, "domainName": "example.com", "matchUser": "", "targetAddresses": ["support@example.com"]},
			],
		},
	}


def test_diff_mode_nothing_to_create(run):
	data, mocks = run(EXISTING_RULES[0], diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
		},
	}


def test_check_mode(run):
	data, mocks = run(NEW_RULE, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_create(run):
	data, mocks = run(EXISTING_RULES[0], check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(run):
	data, mocks = run(NEW_RULE, diff=True, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
				{"prefix": True, "catchall": True, "domainName": "example.com", "matchUser": "", "targetAddresses": ["support@example.com"]},
			],
		},
	}


def test_diff_and_check_modes_nothing_to_create(run):
	data, mocks = run(EXISTING_RULES[0], check_mode=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
		},
	}


def test_normal_create(run):
	data, mocks = run(NEW_RULE)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_create(run):
	data, mocks = run(EXISTING_RULES[0])

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	assert data == {"changed": False}
