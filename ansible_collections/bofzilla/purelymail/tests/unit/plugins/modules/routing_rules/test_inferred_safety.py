# ruff: noqa: E501
import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateRoutingRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules import routing_rules
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import AnsibleFailJson, make_runner  # noqa: F401

EXISTING_RULES = [
	# any_address
	RoutingRule(id=1, match_user="", prefix=True, catchall=False, domain_name="example.com", target_addresses=["admin@example.com"]),
]
assert EXISTING_RULES[0].preset == "any_address"


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
	def inner_run(rules: list[dict], *, canonical: list[str] | None = None, inferred_safety: bool = True, **kwargs):
		canonical_param = {"canonical": canonical} if canonical is not None else {}
		params = {"rules": rules, **canonical_param, "inferred_safety": inferred_safety}
		return runner_run(params=params, **kwargs)

	return inner_run


def test_unknown_preset(run):
	rule = CreateRoutingRequest(catchall=True, prefix=True, match_user="toto", domain_name="example.com", target_addresses=[])  # ty: ignore[missing-argument]
	assert rule.preset is None

	data, _ = run(
		[rule.as_playbook_input()],
		inferred_safety=True,
		expect=AnsibleFailJson,
	)
	assert data == {"msg": "Rule nº0 doesn't match any existing preset."}


def test_conflict_any_rule_canonical(run):
	data, _ = run(
		[{"preset": "any_address", "domain_name": "example.com", "target_addresses": []}],
		canonical=["example.com"],
		inferred_safety=True,
		expect=AnsibleFailJson,
	)

	assert data == {"msg": "Rule #0: only one `any_address` or `catchall_except_valid` rule is allowed per domain (example.com)."}


def test_conflict_catchall_rule_canonical(run):
	data, _ = run(
		[{"preset": "catchall_except_valid", "domain_name": "example.com", "target_addresses": []}],
		canonical=["example.com"],
		inferred_safety=True,
		expect=AnsibleFailJson,
	)

	assert data == {"msg": "Rule #0: only one `any_address` or `catchall_except_valid` rule is allowed per domain (example.com)."}
