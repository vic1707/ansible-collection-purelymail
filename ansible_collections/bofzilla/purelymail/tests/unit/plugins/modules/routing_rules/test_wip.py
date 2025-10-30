import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules import routing_rules
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_RULES = [
	RoutingRule(id=1, matchUser="toto", prefix=True, catchall=False, domainName="example.com", targetAddresses=["admin@example.com"]),
	RoutingRule(id=2, matchUser="admin", prefix=True, catchall=False, domainName="example.com", targetAddresses=["support@example.com"]),
]

EXISTING_RULES_AS_INPUT = [r.dump(by_alias=True, exclude=["id"]) for r in EXISTING_RULES]
NEW_RULE = dict(
	domain_name="example.com",
	match_user="newuser",
	prefix=False,
	catchall=False,
	target_addresses=["helpdesk@example.com"],
)


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		routing_rules,
		(
			(
				"RoutingClient",
				lambda mock: setattr(mock.list_routing_rules, "return_value", ListRoutingResponse(EXISTING_RULES)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(rules: list[dict], *, canonical: bool, **kwargs):
		params = {"rules": rules, "canonical": canonical}
		return runner_run(params=params, **kwargs)

	return inner_run


def test_noncanonical_changes_normal(run):
	data, mocks = run([NEW_RULE], canonical=False)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": True}


def test_noncanonical_no_changes_normal(run):
	data, mocks = run([EXISTING_RULES_AS_INPUT[0]], canonical=False)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_noncanonical_changes_diff(run):
	data, mocks = run([NEW_RULE], canonical=False, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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
				{"prefix": False, "catchall": False, "domainName": "example.com", "matchUser": "newuser", "targetAddresses": ["helpdesk@example.com"]},
			],
		},
	}


def test_noncanonical_no_changes_diff(run):
	data, mocks = run([EXISTING_RULES_AS_INPUT[0]], canonical=False, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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


def test_noncanonical_changes_check(run):
	data, mocks = run([NEW_RULE], canonical=False, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": True}


def test_noncanonical_no_changes_check(run):
	data, mocks = run([EXISTING_RULES_AS_INPUT[0]], canonical=False, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_noncanonical_changes_diff_check(run):
	data, mocks = run([NEW_RULE], canonical=False, check_mode=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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
				{"prefix": False, "catchall": False, "domainName": "example.com", "matchUser": "newuser", "targetAddresses": ["helpdesk@example.com"]},
			],
		},
	}


def test_noncanonical_no_changes_diff_check(run):
	data, mocks = run([EXISTING_RULES_AS_INPUT[0]], canonical=False, check_mode=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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


def test_canonical_changes_normal(run):
	data, mocks = run([NEW_RULE], canonical=True)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	assert mocks["RoutingClient"].delete_routing_rule.call_count == 2
	assert data == {"changed": True}


def test_canonical_no_changes_normal(run):
	data, mocks = run(EXISTING_RULES_AS_INPUT, canonical=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_canonical_changes_diff(run):
	data, mocks = run([NEW_RULE], canonical=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	assert mocks["RoutingClient"].delete_routing_rule.call_count == 2

	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": False, "catchall": False, "domainName": "example.com", "matchUser": "newuser", "targetAddresses": ["helpdesk@example.com"]},
			],
		},
	}


def test_canonical_no_changes_diff(run):
	data, mocks = run(EXISTING_RULES_AS_INPUT, canonical=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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


def test_canonical_changes_check(run):
	data, mocks = run([NEW_RULE], canonical=True, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": True}


def test_canonical_no_changes_check(run):
	data, mocks = run(EXISTING_RULES_AS_INPUT, canonical=True, check_mode=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {"changed": False}


def test_canonical_changes_diff_check(run):
	data, mocks = run([NEW_RULE], canonical=True, check_mode=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"]},
				{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"]},
			],
			"after": [
				{"prefix": False, "catchall": False, "domainName": "example.com", "matchUser": "newuser", "targetAddresses": ["helpdesk@example.com"]},
			],
		},
	}


def test_canonical_no_changes_diff_check(run):
	data, mocks = run(EXISTING_RULES_AS_INPUT, canonical=True, check_mode=True, diff=True)

	mocks["RoutingClient"].create_routing_rule.assert_not_called()
	mocks["RoutingClient"].delete_routing_rule.assert_not_called()

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
