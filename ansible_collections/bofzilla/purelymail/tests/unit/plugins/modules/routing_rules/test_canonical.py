import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules import routing_rules
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_RULES = [
	RoutingRule(id=1, match_user="toto", prefix=True, catchall=False, domain_name="toto.com", target_addresses=["admin@toto.com"]),
	RoutingRule(id=2, match_user="admin", prefix=True, catchall=False, domain_name="example.com", target_addresses=["support@example.com"]),
]

EXISTING_RULES_AS_INPUT = [r.as_playbook_input() for r in EXISTING_RULES]
NEW_RULE_TOTO = dict(
	domain_name="toto.com",
	match_user="newuser",
	prefix=False,
	catchall=False,
	target_addresses=["helpdesk@toto.com"],
)
NEW_RULE_EXAMPLE = dict(
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
	def inner_run(rules: list[dict], *, canonical: list[str] | None, **kwargs):
		params = {"rules": rules, **({"canonical": canonical} if canonical is not None else {})}
		return runner_run(params=params, **kwargs)

	return inner_run


def test_absent_canonical_means_canonical_for_all(run):
	data, mocks = run([], canonical=None)

	assert mocks["RoutingClient"].delete_routing_rule.call_count == 2
	assert data == {"changed": True, "rules": []}


def test_canonical_empty_list_disables_prune(run):
	data, mocks = run([], canonical=[])

	mocks["RoutingClient"].delete_routing_rule.assert_not_called()
	assert data == {
		"changed": False,
		"rules": [
			{"prefix": True, "catchall": False, "domainName": "toto.com", "matchUser": "toto", "targetAddresses": ["admin@toto.com"], "preset": "prefix_match"},
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "preset": "prefix_match"},
		],
	}


def test_canonical_subset_only_prunes_for_that_domain(run):
	data, mocks = run([NEW_RULE_TOTO], canonical=["toto.com"])

	mocks["RoutingClient"].delete_routing_rule.assert_called_once()
	mocks["RoutingClient"].create_routing_rule.assert_called_once()
	assert data == {
		"changed": True,
		"rules": [
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "preset": "prefix_match"},
			{"prefix": False, "catchall": False, "domainName": "toto.com", "matchUser": "newuser", "targetAddresses": ["helpdesk@toto.com"], "preset": "exact_match"},
		],
	}
