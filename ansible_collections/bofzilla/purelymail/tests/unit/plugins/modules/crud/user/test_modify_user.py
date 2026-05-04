import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import GetUserResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import modify_user
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

CURRENT_USER = GetUserResponse(
	enableSearchIndexing=True,
	recoveryEnabled=True,
	requireTwoFactorAuthentication=False,
	enableSpamFiltering=True,
	resetMethods=[],
)


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		modify_user,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.get_user, "return_value", CURRENT_USER),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(params: dict, **kwargs):
		params.setdefault("user_name", "user@example.com")
		return runner_run(params=params, **kwargs)

	return inner_run


def test_no_changes_provided(run):
	# only user_name provided, nothing to change
	data, mocks = run({})

	mocks["UserClient"].modify_user.assert_not_called()
	mocks["UserClient"].get_user.assert_not_called()
	assert data == {"changed": False}


def test_no_changes_provided_diff(run):
	data, _ = run({}, diff=True)
	assert data == {"changed": False, "diff": {"before": {}, "after": {}}}


def test_change_search_indexing(run):
	data, mocks = run({"enable_search_indexing": False})

	mocks["UserClient"].modify_user.assert_called_once()
	assert data == {"changed": True}


def test_change_search_indexing_idempotent(run):
	data, mocks = run({"enable_search_indexing": True})  # already True

	mocks["UserClient"].modify_user.assert_not_called()
	assert data == {"changed": False}


def test_change_2fa(run):
	data, mocks = run({"require_two_factor_authentication": True})

	mocks["UserClient"].modify_user.assert_called_once()
	assert data == {"changed": True}


def test_change_password_reset_idempotent(run):
	# recoveryEnabled=True maps to enable_password_reset=True
	data, mocks = run({"enable_password_reset": True})

	mocks["UserClient"].modify_user.assert_not_called()
	assert data == {"changed": False}


def test_change_password_reset(run):
	data, mocks = run({"enable_password_reset": False})

	mocks["UserClient"].modify_user.assert_called_once()
	assert data == {"changed": True}


def test_new_password_always_changed(run):
	data, mocks = run({"new_password": "secret123"})

	mocks["UserClient"].modify_user.assert_called_once()
	assert data == {"changed": True}


def test_new_password_check_mode(run):
	data, mocks = run({"new_password": "secret123"}, check_mode=True)

	mocks["UserClient"].modify_user.assert_not_called()
	assert data == {"changed": True}


def test_new_user_name_change(run):
	data, mocks = run({"new_user_name": "renamed@example.com"})

	mocks["UserClient"].modify_user.assert_called_once()
	assert data == {"changed": True}


def test_new_user_name_idempotent(run):
	# new_user_name equal to current user_name → no rename
	data, mocks = run({"new_user_name": "user@example.com"})

	mocks["UserClient"].modify_user.assert_not_called()
	assert data == {"changed": False}


def test_diff(run):
	data, _ = run({"enable_search_indexing": False, "require_two_factor_authentication": True}, diff=True)

	assert data["changed"] is True
	assert data["diff"]["before"] == {"enableSearchIndexing": True, "requireTwoFactorAuthentication": False}
	assert data["diff"]["after"] == {"enableSearchIndexing": False, "requireTwoFactorAuthentication": True}


def test_diff_with_password(run):
	data, _ = run({"new_password": "secret123"}, diff=True)

	assert data["changed"] is True
	assert data["diff"]["before"] == {"newPassword": "<unknown>"}
	assert data["diff"]["after"] == {"newPassword": "<changed>"}


def test_check_mode(run):
	data, mocks = run({"enable_search_indexing": False}, check_mode=True)

	mocks["UserClient"].modify_user.assert_not_called()
	assert data == {"changed": True}


def test_check_and_diff(run):
	data, mocks = run({"enable_search_indexing": False}, check_mode=True, diff=True)

	mocks["UserClient"].modify_user.assert_not_called()
	assert data["changed"] is True
	assert data["diff"]["after"] == {"enableSearchIndexing": False}
