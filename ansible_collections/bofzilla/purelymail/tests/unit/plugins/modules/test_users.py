import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import ModifyUserRequest, UpsertPasswordResetRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import GetUserResponse, ListPasswordResetResponse, ListUsersResponse
from ansible_collections.bofzilla.purelymail.plugins.modules import users
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401


def _existing_user(
	enableSearchIndexing: bool = True,
	recoveryEnabled: bool = True,
	requireTwoFactorAuthentication: bool = False,
) -> GetUserResponse:
	return GetUserResponse(
		enableSearchIndexing=enableSearchIndexing,
		recoveryEnabled=recoveryEnabled,
		requireTwoFactorAuthentication=requireTwoFactorAuthentication,
		enableSpamFiltering=True,
		resetMethods=[],
	)


def _setup_default(mock):
	# default: 'alice@example.com' already exists, 'bob@example.com' does not.
	mock.list_users.return_value = ListUsersResponse(users=["alice@example.com"])
	mock.get_user.return_value = _existing_user()
	mock.list_password_reset.return_value = ListPasswordResetResponse(users=[])


def _setup_with_methods(methods):
	def _setup(mock):
		mock.list_users.return_value = ListUsersResponse(users=["alice@example.com"])
		mock.get_user.return_value = _existing_user()
		mock.list_password_reset.return_value = ListPasswordResetResponse(users=methods)

	return _setup


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(users, (("UserClient", _setup_default),))

	@functools.wraps(runner_run)
	def inner_run(params: dict, **kwargs):
		params.setdefault("canonical", False)
		params.setdefault("password_mode", "update-if-provided")
		# fill defaults the way AnsibleModule normally would
		for u in params.get("users", []):
			u.setdefault("enable_search_indexing", True)
			u.setdefault("enable_password_reset", True)
			u.setdefault("require_two_factor_authentication", False)
			u.setdefault("recovery_email", "")
			u.setdefault("recovery_email_description", "")
			u.setdefault("recovery_email_allow_mfa_reset", True)
			u.setdefault("recovery_phone", "")
			u.setdefault("recovery_phone_description", "")
			u.setdefault("recovery_phone_allow_mfa_reset", True)
			u.setdefault("send_welcome_email", False)
		return runner_run(params=params, **kwargs)

	return inner_run


# ---------------------------------------------------------------------------
# basic idempotency
# ---------------------------------------------------------------------------


def test_no_changes(run):
	data, mocks = run({"users": [{"name": "alice@example.com"}]})
	mocks["UserClient"].create_user.assert_not_called()
	mocks["UserClient"].modify_user.assert_not_called()
	mocks["UserClient"].delete_user.assert_not_called()
	mocks["UserClient"].upsert_password_reset.assert_not_called()
	mocks["UserClient"].delete_password_reset.assert_not_called()
	assert data["changed"] is False


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


def test_create_new_user(run):
	data, mocks = run(
		{
			"users": [
				{"name": "alice@example.com"},
				{"name": "bob@example.com", "password": "s3cret"},
			],
		}
	)
	mocks["UserClient"].create_user.assert_called_once()
	created_req = mocks["UserClient"].create_user.call_args.args[0]
	assert created_req.userName == "bob"
	assert created_req.domainName == "example.com"
	assert created_req.password == "s3cret"
	assert data["changed"] is True
	assert "bob@example.com" in data["users"]


def test_create_with_recovery_passes_through(run):
	data, mocks = run(
		{
			"users": [
				{"name": "alice@example.com"},
				{
					"name": "bob@example.com",
					"password": "s3cret",
					"recovery_email": "bob-recovery@example.com",
					"recovery_email_description": "backup",
				},
			],
		}
	)
	mocks["UserClient"].create_user.assert_called_once()
	created_req = mocks["UserClient"].create_user.call_args.args[0]
	assert created_req.recoveryEmail == "bob-recovery@example.com"
	assert created_req.recoveryEmailDescription == "backup"
	# upsert is NOT called for new users (recovery handled inline at create)
	mocks["UserClient"].upsert_password_reset.assert_not_called()
	assert data["changed"] is True


def test_create_missing_password_fails(run):
	_, _ = run({"users": [{"name": "bob@example.com"}]}, expect=BaseException)


# ---------------------------------------------------------------------------
# canonical
# ---------------------------------------------------------------------------


def test_canonical_deletes_extras(run):
	data, mocks = run({"canonical": True, "users": []})
	mocks["UserClient"].delete_user.assert_called_once()
	deleted_req = mocks["UserClient"].delete_user.call_args.args[0]
	assert deleted_req.userName == "alice@example.com"
	assert data["changed"] is True


def test_non_canonical_keeps_extras(run):
	data, mocks = run({"canonical": False, "users": []})
	mocks["UserClient"].delete_user.assert_not_called()
	assert data["changed"] is False


# ---------------------------------------------------------------------------
# modify settings
# ---------------------------------------------------------------------------


def test_modify_settings(run):
	data, mocks = run(
		{
			"users": [
				{"name": "alice@example.com", "enable_search_indexing": False, "require_two_factor_authentication": True},
			],
		}
	)
	mocks["UserClient"].modify_user.assert_called_once()
	req: ModifyUserRequest = mocks["UserClient"].modify_user.call_args.args[0]
	assert req.enableSearchIndexing is False
	assert req.requireTwoFactorAuthentication is True
	assert req.newPassword is None
	assert data["changed"] is True


def test_modify_idempotent(run):
	data, mocks = run({"users": [{"name": "alice@example.com"}]})  # all defaults match
	mocks["UserClient"].modify_user.assert_not_called()
	assert data["changed"] is False


# ---------------------------------------------------------------------------
# password mode
# ---------------------------------------------------------------------------


def test_password_update_if_provided(run):
	data, mocks = run({"users": [{"name": "alice@example.com", "password": "rotated"}]})
	mocks["UserClient"].modify_user.assert_called_once()
	req: ModifyUserRequest = mocks["UserClient"].modify_user.call_args.args[0]
	assert req.newPassword == "rotated"
	assert data["changed"] is True


def test_password_ignore_if_exists(run):
	data, mocks = run(
		{
			"password_mode": "ignore-if-exists",
			"users": [{"name": "alice@example.com", "password": "rotated"}],
		}
	)
	mocks["UserClient"].modify_user.assert_not_called()
	assert data["changed"] is False


def test_per_user_password_mode_override(run):
	data, mocks = run(
		{
			"password_mode": "ignore-if-exists",
			"users": [{"name": "alice@example.com", "password": "rotated", "password_mode": "update-if-provided"}],
		}
	)
	mocks["UserClient"].modify_user.assert_called_once()
	assert data["changed"] is True


# ---------------------------------------------------------------------------
# recovery method reconciliation (existing user)
# ---------------------------------------------------------------------------


def _params_with_user(**user_overrides):
	user = {
		"name": "alice@example.com",
		"enable_search_indexing": True,
		"enable_password_reset": True,
		"require_two_factor_authentication": False,
		"recovery_email": "",
		"recovery_email_description": "",
		"recovery_email_allow_mfa_reset": True,
		"recovery_phone": "",
		"recovery_phone_description": "",
		"recovery_phone_allow_mfa_reset": True,
		"send_welcome_email": False,
	}
	user.update(user_overrides)
	return {"canonical": False, "password_mode": "update-if-provided", "users": [user]}


def test_recovery_email_added(make_runner):  # noqa: F811
	# no current methods, declare an email recovery → should upsert
	runner = make_runner(users, (("UserClient", _setup_with_methods([])),))
	data, mocks = runner(params=_params_with_user(recovery_email="r@example.com", recovery_email_description="bk"))
	mocks["UserClient"].upsert_password_reset.assert_called_once()
	req: UpsertPasswordResetRequest = mocks["UserClient"].upsert_password_reset.call_args.args[0]
	assert req.type == "email"
	assert req.target == "r@example.com"
	assert req.description == "bk"
	assert req.allowMfaReset is True
	mocks["UserClient"].delete_password_reset.assert_not_called()
	assert data["changed"] is True


def test_recovery_email_idempotent(make_runner):  # noqa: F811
	current = [ListPasswordResetResponseItem(type="email", target="r@example.com", description="bk", allowMfaReset=True)]
	runner = make_runner(users, (("UserClient", _setup_with_methods(current)),))
	data, mocks = runner(params=_params_with_user(recovery_email="r@example.com", recovery_email_description="bk"))
	mocks["UserClient"].upsert_password_reset.assert_not_called()
	mocks["UserClient"].delete_password_reset.assert_not_called()
	assert data["changed"] is False


def test_recovery_email_replaced_when_target_changes(make_runner):  # noqa: F811
	current = [ListPasswordResetResponseItem(type="email", target="old@example.com", description="", allowMfaReset=True)]
	runner = make_runner(users, (("UserClient", _setup_with_methods(current)),))
	data, mocks = runner(params=_params_with_user(recovery_email="new@example.com"))
	# old removed, new added
	mocks["UserClient"].delete_password_reset.assert_called_once()
	deleted = mocks["UserClient"].delete_password_reset.call_args.args[0]
	assert deleted.target == "old@example.com"
	mocks["UserClient"].upsert_password_reset.assert_called_once()
	added = mocks["UserClient"].upsert_password_reset.call_args.args[0]
	assert added.target == "new@example.com"
	assert data["changed"] is True


def test_empty_recovery_email_deletes_existing(make_runner):  # noqa: F811
	current = [ListPasswordResetResponseItem(type="email", target="old@example.com", description="", allowMfaReset=True)]
	runner = make_runner(users, (("UserClient", _setup_with_methods(current)),))
	data, mocks = runner(params=_params_with_user())  # both recovery_* default to ""
	mocks["UserClient"].delete_password_reset.assert_called_once()
	mocks["UserClient"].upsert_password_reset.assert_not_called()
	assert data["changed"] is True


def test_recovery_phone(make_runner):  # noqa: F811
	runner = make_runner(users, (("UserClient", _setup_with_methods([])),))
	data, mocks = runner(params=_params_with_user(recovery_phone="+33123456789"))
	mocks["UserClient"].upsert_password_reset.assert_called_once()
	req: UpsertPasswordResetRequest = mocks["UserClient"].upsert_password_reset.call_args.args[0]
	assert req.type == "phone"
	assert req.target == "+33123456789"
	assert data["changed"] is True


def test_allow_mfa_reset_flag(make_runner):  # noqa: F811
	current = [ListPasswordResetResponseItem(type="email", target="r@example.com", description="", allowMfaReset=True)]
	runner = make_runner(users, (("UserClient", _setup_with_methods(current)),))
	data, mocks = runner(params=_params_with_user(recovery_email="r@example.com", recovery_email_allow_mfa_reset=False))
	# mismatch on allowMfaReset → delete + add
	mocks["UserClient"].delete_password_reset.assert_called_once()
	mocks["UserClient"].upsert_password_reset.assert_called_once()
	added = mocks["UserClient"].upsert_password_reset.call_args.args[0]
	assert added.allowMfaReset is False
	assert data["changed"] is True


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------


def test_invalid_name_no_at(run):
	_, _ = run({"users": [{"name": "no-at-sign"}]}, expect=BaseException)


def test_duplicate_names(run):
	_, _ = run(
		{
			"users": [
				{"name": "alice@example.com"},
				{"name": "alice@example.com"},
			],
		},
		expect=BaseException,
	)


# ---------------------------------------------------------------------------
# diff & check_mode
# ---------------------------------------------------------------------------


def test_diff(run):
	data, _ = run(
		{
			"users": [
				{"name": "alice@example.com", "enable_search_indexing": False},
				{"name": "bob@example.com", "password": "x"},
			],
		},
		diff=True,
	)
	assert data["changed"] is True
	assert "diff" in data
	assert "alice@example.com" in data["diff"]["before"]["users"]
	assert "bob@example.com" in data["diff"]["after"]["users"]


def test_check_mode_no_side_effects(run):
	_, mocks = run(
		{
			"users": [
				{"name": "alice@example.com", "enable_search_indexing": False},
				{"name": "bob@example.com", "password": "x"},
			],
		},
		check_mode=True,
	)
	mocks["UserClient"].create_user.assert_not_called()
	mocks["UserClient"].modify_user.assert_not_called()
	mocks["UserClient"].delete_user.assert_not_called()
	mocks["UserClient"].upsert_password_reset.assert_not_called()
	mocks["UserClient"].delete_password_reset.assert_not_called()
