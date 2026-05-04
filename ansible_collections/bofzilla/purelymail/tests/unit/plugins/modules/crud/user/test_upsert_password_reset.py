import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListPasswordResetResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import upsert_password_reset
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING = [
	ListPasswordResetResponseItem(type="email", target="a@b.com", description="primary", allowMfaReset=True),
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		upsert_password_reset,
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
		return runner_run(params=params, **kwargs)

	return inner_run


def test_create_new(run):
	data, mocks = run({"type": "email", "target": "new@x.com", "description": "x", "allow_mfa_reset": True})

	mocks["UserClient"].upsert_password_reset.assert_called_once()
	assert data == {"changed": True}


def test_idempotent_existing(run):
	data, mocks = run({"type": "email", "target": "a@b.com", "description": "primary", "allow_mfa_reset": True})

	mocks["UserClient"].upsert_password_reset.assert_not_called()
	assert data == {"changed": False}


def test_update_existing_description(run):
	data, mocks = run({"type": "email", "target": "a@b.com", "description": "newdesc", "allow_mfa_reset": True})

	mocks["UserClient"].upsert_password_reset.assert_called_once()
	assert data == {"changed": True}


def test_update_with_existing_target(run):
	# Replacing a@b.com → c@d.com via existing_target
	data, mocks = run(
		{
			"type": "email",
			"target": "c@d.com",
			"existing_target": "a@b.com",
			"description": "primary",
			"allow_mfa_reset": True,
		}
	)

	mocks["UserClient"].upsert_password_reset.assert_called_once()
	assert data == {"changed": True}


def test_check_mode(run):
	data, mocks = run({"type": "email", "target": "new@x.com"}, check_mode=True)

	mocks["UserClient"].upsert_password_reset.assert_not_called()
	assert data == {"changed": True}


def test_diff_create(run):
	data, _ = run({"type": "email", "target": "new@x.com", "description": "d", "allow_mfa_reset": False}, diff=True)

	assert data["changed"] is True
	assert data["diff"]["before"] == [{"type": "email", "target": "a@b.com", "description": "primary", "allowMfaReset": True}]
	assert data["diff"]["after"] == [
		{"type": "email", "target": "a@b.com", "description": "primary", "allowMfaReset": True},
		{"type": "email", "target": "new@x.com", "description": "d", "allowMfaReset": False},
	]


def test_diff_idempotent(run):
	data, _ = run({"type": "email", "target": "a@b.com", "description": "primary", "allow_mfa_reset": True}, diff=True)

	assert data["changed"] is False
	assert data["diff"]["before"] == data["diff"]["after"]
