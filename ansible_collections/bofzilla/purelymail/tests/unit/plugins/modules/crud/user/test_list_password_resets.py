import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListPasswordResetResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import list_password_resets
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING = [
	ListPasswordResetResponseItem(type="email", target="a@b.com", description="primary", allowMfaReset=True),
	ListPasswordResetResponseItem(type="phone", target="+33000000", description="phone", allowMfaReset=False),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		list_password_resets,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.list_password_reset, "return_value", ListPasswordResetResponse(EXISTING)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(**kwargs):
		return runner_run(params={"user_name": "user@example.com"}, **kwargs)

	return inner_run


EXPECTED = [
	{"type": "email", "target": "a@b.com", "description": "primary", "allowMfaReset": True},
	{"type": "phone", "target": "+33000000", "description": "phone", "allowMfaReset": False},
]


def test_normal(run):
	data, _ = run()
	assert data == {"changed": False, "methods": EXPECTED}


def test_check_mode(run):
	data, _ = run(check_mode=True)
	assert data == {"changed": False}


def test_diff(run):
	data, _ = run(diff=True)
	assert data == {"changed": False, "methods": EXPECTED, "diff": {"before": EXPECTED, "after": EXPECTED}}


def test_check_and_diff(run):
	data, _ = run(check_mode=True, diff=True)
	assert data == {"changed": False, "diff": {"before": EXPECTED, "after": EXPECTED}}
