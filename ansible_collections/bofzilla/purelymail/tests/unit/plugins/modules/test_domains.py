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

