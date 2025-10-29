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
