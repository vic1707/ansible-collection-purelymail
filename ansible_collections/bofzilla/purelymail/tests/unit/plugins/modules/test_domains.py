import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainDnsSummary, ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListDomainsResponse
from ansible_collections.bofzilla.purelymail.plugins.modules import domains
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

STATE = ListDomainsResponse(
	[
		ApiDomainInfo(name="example.com", allowAccountReset=True, symbolicSubaddressing=True, isShared=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
		ApiDomainInfo(name="testdomain.net", allowAccountReset=False, symbolicSubaddressing=False, isShared=True, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
		ApiDomainInfo(name="another.org", allowAccountReset=True, symbolicSubaddressing=False, isShared=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
	]
)


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		domains,
		(
			(
				"DomainClient",
				lambda mock: setattr(mock.list_domains, "return_value", STATE),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(domains: list[dict], *, canonical: bool, **kwargs):
		return runner_run(params={"domains": domains, "canonical": canonical}, **kwargs)

	return inner_run


def test_noncanonical_adds_missing(run):
	data, mocks = run(
		[{"name": "new.com"}],
		canonical=False,
	)

	mocks["DomainClient"].add_domain.assert_called_once()
	mocks["DomainClient"].delete_domain.assert_not_called()
	mocks["DomainClient"].update_domain_settings.assert_not_called()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "new.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_noncanonical_no_changes(run):
	data, mocks = run(
		[{"name": "example.com"}],
		canonical=False,
	)

	mocks["DomainClient"].add_domain.assert_not_called()
	mocks["DomainClient"].delete_domain.assert_not_called()
	mocks["DomainClient"].update_domain_settings.assert_not_called()

	assert data == {
		"changed": False,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_noncanonical_updates(run):
	data, mocks = run(
		[{"name": "example.com", "symbolic_subaddressing": False}],
		canonical=False,
	)

	mocks["DomainClient"].update_domain_settings.assert_called_once()
	mocks["DomainClient"].add_domain.assert_not_called()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_noncanonical_diff(run):
	data, mocks = run(
		[{"name": "new.com"}],
		canonical=False,
		diff=True,
	)

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "new.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
		"diff": {
			"before": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": True,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "testdomain.net",
					"allowAccountReset": False,
					"symbolicSubaddressing": False,
					"isShared": True,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "another.org",
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
					"symbolicSubaddressing": True,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "testdomain.net",
					"allowAccountReset": False,
					"symbolicSubaddressing": False,
					"isShared": True,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "another.org",
					"allowAccountReset": True,
					"symbolicSubaddressing": False,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "new.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": True,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
			],
		},
	}


def test_noncanonical_check_mode(run):
	data, mocks = run(
		[{"name": "new.com"}],
		canonical=False,
		check_mode=True,
	)

	mocks["DomainClient"].add_domain.assert_not_called()
	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "new.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_canonical_removes_extra(run):
	data, mocks = run([{"name": "example.com"}], canonical=True)

	assert mocks["DomainClient"].delete_domain.call_count == 2
	mocks["DomainClient"].add_domain.assert_not_called()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			}
		],
	}


def test_canonical_no_changes(run):
	input_domains = [
		{"name": "example.com"},
		{"name": "testdomain.net"},
		{"name": "another.org"},
	]

	data, mocks = run(input_domains, canonical=True)

	mocks["DomainClient"].add_domain.assert_not_called()
	mocks["DomainClient"].delete_domain.assert_not_called()
	mocks["DomainClient"].update_domain_settings.assert_not_called()

	assert data == {
		"changed": False,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_canonical_adds_and_deletes(run):
	data, mocks = run(
		[{"name": "example.com"}, {"name": "new.com"}],
		canonical=True,
	)

	mocks["DomainClient"].add_domain.assert_called_once()
	assert mocks["DomainClient"].delete_domain.call_count == 2

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "new.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_canonical_diff(run):
	data, mocks = run(
		[{"name": "example.com"}],
		canonical=True,
		diff=True,
	)

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			}
		],
		"diff": {
			"before": [
				{
					"name": "example.com",
					"allowAccountReset": True,
					"symbolicSubaddressing": True,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "testdomain.net",
					"allowAccountReset": False,
					"symbolicSubaddressing": False,
					"isShared": True,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				},
				{
					"name": "another.org",
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
					"symbolicSubaddressing": True,
					"isShared": False,
					"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
				}
			],
		},
	}


def test_canonical_check_mode(run):
	data, mocks = run(
		[],
		canonical=True,
		check_mode=True,
	)

	mocks["DomainClient"].add_domain.assert_not_called()
	mocks["DomainClient"].delete_domain.assert_not_called()

	assert data == {"changed": True, "domains": []}


def test_canonical_partial_overlap(run):
	data, mocks = run(
		[{"name": "example.com"}, {"name": "new.com"}],
		canonical=True,
	)

	mocks["DomainClient"].add_domain.assert_called_once()
	mocks["DomainClient"].delete_domain.assert_called()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "new.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_dns_recheck_noncanonical(run):
	data, mocks = run(
		[{"name": "example.com", "recheck_dns": True}],
		canonical=False,
	)

	mocks["DomainClient"].update_domain_settings.assert_called_once()
	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_dns_recheck_noncanonical_new_domain(run):
	data, mocks = run(
		[{"name": "brandnew.com", "recheck_dns": True}],
		canonical=False,
	)

	mocks["DomainClient"].add_domain.assert_called_once()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "brandnew.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}


def test_dns_recheck_canonical(run):
	data, mocks = run(
		[{"name": "example.com", "recheck_dns": True}],
		canonical=True,
	)

	mocks["DomainClient"].update_domain_settings.assert_called_once()
	assert mocks["DomainClient"].delete_domain.call_count == 2

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			}
		],
	}


def test_dns_recheck_check_mode(run):
	data, mocks = run(
		[{"name": "example.com", "recheck_dns": True}],
		canonical=False,
		check_mode=True,
	)

	mocks["DomainClient"].update_domain_settings.assert_not_called()

	assert data == {
		"changed": True,
		"domains": [
			{
				"name": "example.com",
				"allowAccountReset": True,
				"symbolicSubaddressing": True,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "testdomain.net",
				"allowAccountReset": False,
				"symbolicSubaddressing": False,
				"isShared": True,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
			{
				"name": "another.org",
				"allowAccountReset": True,
				"symbolicSubaddressing": False,
				"isShared": False,
				"dnsSummary": {"passesMx": True, "passesSpf": True, "passesDkim": True, "passesDmarc": True},
			},
		],
	}
