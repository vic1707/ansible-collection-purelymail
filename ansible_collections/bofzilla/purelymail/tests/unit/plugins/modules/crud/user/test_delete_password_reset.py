import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListPasswordResetResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import delete_password_reset
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING = [
	ListPasswordResetResponseItem(type="email", target="a@b.com", description="primary", allowMfaReset=True),
	ListPasswordResetResponseItem(type="phone", target="+33000000", description="phone", allowMfaReset=False),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		delete_password_reset,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.list_password_reset, "return_value", ListPasswordResetResponse(EXISTING)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(params: dict, **kwargs):
		params.setdefault("user_name", "user@example.com")
		params.setdefault("target", None)
		return runner_run(params=params, **kwargs)

	return inner_run


def test_delete_existing(run):
	data, mocks = run({"target": "a@b.com"})

	mocks["UserClient"].delete_password_reset.assert_called_once()
	assert data == {"changed": True}


def test_delete_unknown_target_idempotent(run):
	data, mocks = run({"target": "missing@example.com"})

	mocks["UserClient"].delete_password_reset.assert_not_called()
	assert data == {"changed": False}


def test_delete_all(run):
	data, mocks = run({})

	mocks["UserClient"].delete_password_reset.assert_called_once()
	assert data == {"changed": True}


def test_check_mode(run):
	data, mocks = run({"target": "a@b.com"}, check_mode=True)

	mocks["UserClient"].delete_password_reset.assert_not_called()
	assert data == {"changed": True}


def test_diff_delete(run):
	data, _ = run({"target": "a@b.com"}, diff=True)

	assert data["changed"] is True
	assert {m["target"] for m in data["diff"]["before"]} == {"a@b.com", "+33000000"}
	assert {m["target"] for m in data["diff"]["after"]} == {"+33000000"}


def test_diff_idempotent(run):
	data, _ = run({"target": "missing@example.com"}, diff=True)

	assert data["changed"] is False
	assert data["diff"]["before"] == data["diff"]["after"]
