from unittest.mock import MagicMock

import pytest
from ansible.plugins.loader import lookup_loader

from ansible_collections.bofzilla.purelymail.plugins.lookup import purelymail_ownership_code
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import GetOwnershipCodeResponse


@pytest.fixture(scope="module")
def lookup_module() -> purelymail_ownership_code.LookupModule:
	monkeypatch = pytest.MonkeyPatch()
	domain_client = MagicMock()
	domain_client.get_ownership_code.return_value = GetOwnershipCodeResponse(code="purelymail_ownership_proof=dQw4w9WgXcQ")
	monkeypatch.setattr(purelymail_ownership_code, "DomainClient", lambda *_, **__: domain_client)

	return lookup_loader.get("bofzilla.purelymail.purelymail_ownership_code")


def test_lookup_success(lookup_module):
	ret = lookup_module.run([], variables={}, api_token="dummy")
	assert isinstance(ret, list)
	assert len(ret) == 1
	assert ret[0].code == "purelymail_ownership_proof=dQw4w9WgXcQ"
	assert ret[0].value == "dQw4w9WgXcQ"


# def test_lookup_missing_token(lookup_module):
# 	ret = lookup_module.run([], variables={}, api_token="dummy")
