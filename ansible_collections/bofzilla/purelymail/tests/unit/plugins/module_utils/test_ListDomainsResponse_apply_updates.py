from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainDnsSummary, ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import UpdateDomainSettingsRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListDomainsResponse

STATE = ListDomainsResponse(
	[
		ApiDomainInfo(name="example.com", allowAccountReset=True, symbolicSubaddressing=True, isShared=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
		ApiDomainInfo(name="testdomain.net", allowAccountReset=False, symbolicSubaddressing=False, isShared=True, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
		ApiDomainInfo(name="another.org", allowAccountReset=True, symbolicSubaddressing=False, isShared=False, dnsSummary=ApiDomainDnsSummary(True, True, True, True)),
	]
)


def test_apply_updates_no_updates():
	updated = STATE.apply_updates([])

	assert updated == STATE
	assert updated is not STATE  # Check that a new ListDomainsResponse object is returned


def test_apply_updates_partial_update():
	updates = [
		UpdateDomainSettingsRequest(name="testdomain.net", allowAccountReset=True, symbolicSubaddressing=True),
	]

	updated = STATE.apply_updates(updates)
	updated_domain = updated.domains[1]

	assert updated_domain.name == "testdomain.net"
	assert updated_domain.allowAccountReset is True
	assert updated_domain.symbolicSubaddressing is True

	# Check that an unrelated domain is unchanged
	assert updated.domains[0] is STATE.domains[0]


def test_consider_update_when_recheckDNS():
	updates = [
		UpdateDomainSettingsRequest(name="testdomain.net", recheckDns=True),
	]

	updated = STATE.apply_updates(updates)

	assert updated.domains[1] is not STATE.domains[1]

	assert updated.domains[0] is STATE.domains[0]


def test_apply_updates_multiple_updates_mixed_fields():
	updates = [
		UpdateDomainSettingsRequest(name="example.com", symbolicSubaddressing=False),
		UpdateDomainSettingsRequest(name="another.org", allowAccountReset=False),
	]

	updated = STATE.apply_updates(updates)

	d0 = updated.domains[0]
	assert d0.symbolicSubaddressing is False
	assert d0.allowAccountReset is True

	d2 = updated.domains[2]
	assert d2.allowAccountReset is False
	assert d2.symbolicSubaddressing is False

	assert updated.domains[1] is STATE.domains[1]


def test_apply_updates_no_match_ignored():
	updates = [
		UpdateDomainSettingsRequest(name="ghost-domain.com", allowAccountReset=False),
	]

	updated = STATE.apply_updates(updates)

	assert updated == STATE
	assert updated.domains[0] is STATE.domains[0]
	assert updated.domains[1] is STATE.domains[1]
