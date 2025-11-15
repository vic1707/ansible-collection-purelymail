import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainDnsSummary, ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListDomainsResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.domain import update_domain_settings
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import AnsibleFailJson, make_runner  # noqa: F401

EXISTING_DOMAINS = [
	ApiDomainInfo(name="example.com", isShared=False, allowAccountReset=True, symbolicSubaddressing=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
]

UPDATED = ApiDomainInfo(name="example.com", isShared=False, allowAccountReset=False, symbolicSubaddressing=True, dnsSummary=ApiDomainDnsSummary(True, True, True, True))


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		update_domain_settings,
		(
			(
				"DomainClient",
				lambda mock: setattr(mock.list_domains, "return_value", ListDomainsResponse(EXISTING_DOMAINS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(params: dict, **kwargs):
		# __include_shared not tested (internal parameter)
		params["__include_shared"] = True
		return runner_run(params=params, **kwargs)

	return inner_run


def test_unknown_domain(run):
	data, _ = run({"name": "doesnotexist.com"}, expect=AnsibleFailJson)

	assert data == {"msg": "Error: domain 'doesnotexist.com' does not exist."}


def test_no_changes(run):
	data, mocks = run({"name": "example.com"})

	mocks["DomainClient"].update_domain_settings.assert_not_called()
	assert data == {"changed": False}


def test_update_settings(run):
	params = {
		"name": "example.com",
		"allow_account_reset": False,
		"symbolic_subaddressing": True,
	}

	data, mocks = run(params)

	mocks["DomainClient"].update_domain_settings.assert_called_once()
	assert data == {"changed": True}


def test_diff(run):
	params = {
		"name": "example.com",
		"allow_account_reset": False,
		"symbolic_subaddressing": True,
	}

	data, mocks = run(params, diff=True)

	mocks["DomainClient"].update_domain_settings.assert_called_once()

	assert data["changed"] is True
	assert "diff" in data
	assert data["diff"]["before"] == EXISTING_DOMAINS[0]
	assert data["diff"]["after"] == UPDATED


def test_diff_and_check_mode(run):
	params = {
		"name": "example.com",
		"allow_account_reset": False,
		"symbolic_subaddressing": True,
	}

	data, mocks = run(params, diff=True, check_mode=True)

	mocks["DomainClient"].update_domain_settings.assert_not_called()

	assert data["changed"] is True
	assert data["diff"]["before"] == EXISTING_DOMAINS[0]
	assert data["diff"]["after"] == UPDATED


def test_recheck_dns_triggers_update(run):
	data, mocks = run({"name": "example.com", "recheck_dns": True})

	mocks["DomainClient"].update_domain_settings.assert_called_once()
	assert data == {"changed": True}


def test_recheck_dns_check_mode(run):
	data, mocks = run({"name": "example.com", "recheck_dns": True}, check_mode=True)

	mocks["DomainClient"].update_domain_settings.assert_not_called()
	assert data == {"changed": True}
