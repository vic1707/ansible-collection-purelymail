import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainDnsSummary, ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListDomainsResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.domain import delete_domain
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_DOMAINS = [
	ApiDomainInfo(name="example.com", isShared=False, allowAccountReset=True, symbolicSubaddressing=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
	ApiDomainInfo(name="example2.com", isShared=False, allowAccountReset=True, symbolicSubaddressing=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		delete_domain,
		(
			(
				"DomainClient",
				lambda mock: setattr(mock.list_domains, "return_value", ListDomainsResponse(EXISTING_DOMAINS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(domain_name: str, **kwargs):
		# __include_shared not tested (internal parameter)
		return runner_run(params={"domain_name": domain_name, "__include_shared": True}, **kwargs)

	return inner_run


def test_diff_mode_successful_delete(run):
	data, mocks = run(EXISTING_DOMAINS[0].name, diff=True)

	mocks["DomainClient"].delete_domain.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
			"after": [
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
		},
	}


def test_diff_mode_nothing_to_delete(run):
	data, mocks = run("unknown.com", diff=True)

	mocks["DomainClient"].delete_domain.assert_not_called()
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
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
			"after": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
		},
	}


def test_check_mode(run):
	data, mocks = run(EXISTING_DOMAINS[0].name, check_mode=True)

	mocks["DomainClient"].delete_domain.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_delete(run):
	data, mocks = run("unknown.com", check_mode=True)

	mocks["DomainClient"].delete_domain.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(run):
	data, mocks = run(EXISTING_DOMAINS[0].name, check_mode=True, diff=True)

	mocks["DomainClient"].delete_domain.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
			"after": [
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
		},
	}


def test_diff_and_check_modes_nothing_to_delete(run):
	data, mocks = run("unknown.com", check_mode=True, diff=True)

	mocks["DomainClient"].delete_domain.assert_not_called()
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
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
			"after": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "example2.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
		},
	}


def test_normal_delete(run):
	data, mocks = run(EXISTING_DOMAINS[0].name)

	mocks["DomainClient"].delete_domain.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_delete(run):
	data, mocks = run("unknown.com")

	mocks["DomainClient"].delete_domain.assert_not_called()
	assert data == {"changed": False}
