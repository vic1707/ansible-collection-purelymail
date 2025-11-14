import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import GetOwnershipCodeResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.domain import get_ownership_code
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	return make_runner(
		get_ownership_code,
		(
			(
				"DomainClient",
				lambda mock: setattr(mock.get_ownership_code, "return_value", GetOwnershipCodeResponse(code="purelymail_ownership_proof=dQw4w9WgXcQ")),
			),
		),
	)


def test_diff(run):
	data, _ = run(diff=True)
	assert data == {
		"changed": False,
		"code": "purelymail_ownership_proof=dQw4w9WgXcQ",
		"value": "dQw4w9WgXcQ",
		"diff": {
			"before": {"code": "purelymail_ownership_proof=dQw4w9WgXcQ", "value": "dQw4w9WgXcQ"},
			"after": {"code": "purelymail_ownership_proof=dQw4w9WgXcQ", "value": "dQw4w9WgXcQ"},
		},
	}


def test_check(run):
	data, _ = run(check_mode=True)
	assert data == {"changed": False}


def test_check_and_diff(run):
	data, _ = run(diff=True, check_mode=True)
	assert data == {
		"changed": False,
		"diff": {
			"before": {"code": "purelymail_ownership_proof=dQw4w9WgXcQ", "value": "dQw4w9WgXcQ"},
			"after": {"code": "purelymail_ownership_proof=dQw4w9WgXcQ", "value": "dQw4w9WgXcQ"},
		},
	}


def test_normal(run):
	data, _ = run()
	assert data == {"changed": False, "code": "purelymail_ownership_proof=dQw4w9WgXcQ", "value": "dQw4w9WgXcQ"}
