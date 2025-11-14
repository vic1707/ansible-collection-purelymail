import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainDnsSummary, ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListDomainsResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.domain import list_domains
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_DOMAINS = [
	ApiDomainInfo(name="example.com", isShared=False, allowAccountReset=True, symbolicSubaddressing=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		list_domains,
		(
			(
				"DomainClient",
				lambda mock: setattr(mock.list_domains, "return_value", ListDomainsResponse(EXISTING_DOMAINS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(**kwargs):
		# include_shared doesn't matter as we don't test purelymail's API
		# only this module behaviors
		return runner_run(params={"include_shared": True}, **kwargs)

	return inner_run


def test_diff(run):
	data, _ = run(diff=True)

	assert data == {
		"changed": False,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			}
		],
		"diff": {
			"before": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
			"after": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
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
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
			"after": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
		},
	}


def test_normal_nonshared(run):
	data, _ = run()

	assert data == {
		"changed": False,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_normal(run):
	data, _ = run()

	assert data == {
		"changed": False,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			}
		],
	}
