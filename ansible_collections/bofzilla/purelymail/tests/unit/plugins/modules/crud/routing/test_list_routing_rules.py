import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListRoutingResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.routing import list_routing_rules
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_RULES = [
	RoutingRule(id=1, match_user="toto", prefix=True, catchall=False, domain_name="example.com", target_addresses=["admin@example.com"]),
	RoutingRule(id=2, match_user="admin", prefix=True, catchall=False, domain_name="example.com", target_addresses=["support@example.com"]),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	return make_runner(
		list_routing_rules,
		(
			(
				"RoutingClient",
				lambda mock: setattr(mock.list_routing_rules, "return_value", ListRoutingResponse(EXISTING_RULES)),
			),
		),
	)


def test_diff(run):
	data, _ = run(diff=True)
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


def test_check(run):
	data, _ = run(check_mode=True)
	assert data == {"changed": False}


def test_check_and_diff(run):
	data, _ = run(check_mode=True, diff=True)
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


def test_normal(run):
	data, _ = run()
	assert data == {
		"changed": False,
		"rules": [
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1},
			{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "admin", "targetAddresses": ["support@example.com"], "id": 2},
		],
	}
