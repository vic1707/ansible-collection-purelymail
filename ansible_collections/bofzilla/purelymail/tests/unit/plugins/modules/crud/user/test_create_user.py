import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListUsersResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import create_user
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_USERS = [
	"admin@example.com",
	"admin@example2.com",
]


def mock_user(user_name: str, domain_name: str):
	return {
		"user_name": user_name,
		"domain_name": domain_name,
		"password": "dQw4w9WgXcQ",
		"enable_password_reset": False,
		"recovery_email": "",
		"recovery_email_description": "",
		"recovery_phone": "",
		"recovery_phone_description": "",
		"enable_search_indexing": False,
		"send_welcome_email": False,
	}


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		create_user,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.list_users, "return_value", ListUsersResponse(EXISTING_USERS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(params: dict, **kwargs):
		return runner_run(params=params, **kwargs)

	return inner_run


def test_diff_mode_successful_create(run):
	data, mocks = run(mock_user("toto", "newuser.com"), diff=True)

	mocks["UserClient"].create_user.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": ["admin@example.com", "admin@example2.com"],
			"after": ["admin@example.com", "admin@example2.com", "toto@newuser.com"],
		},
	}


def test_diff_mode_nothing_to_create(run):
	data, mocks = run(mock_user(*EXISTING_USERS[0].split("@")), diff=True)

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": ["admin@example.com", "admin@example2.com"],
			"after": ["admin@example.com", "admin@example2.com"],
		},
	}


def test_check_mode(run):
	data, mocks = run(mock_user("toto", "newuser.com"), check_mode=True)

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_create(run):
	data, mocks = run(mock_user(*EXISTING_USERS[0].split("@")), check_mode=True)

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(run):
	data, mocks = run(mock_user("toto", "newuser.com"), diff=True, check_mode=True)

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": ["admin@example.com", "admin@example2.com"],
			"after": ["admin@example.com", "admin@example2.com", "toto@newuser.com"],
		},
	}


def test_diff_and_check_modes_nothing_to_create(run):
	data, mocks = run(mock_user(*EXISTING_USERS[0].split("@")), check_mode=True, diff=True)

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": ["admin@example.com", "admin@example2.com"],
			"after": ["admin@example.com", "admin@example2.com"],
		},
	}


def test_normal_create(run):
	data, mocks = run(mock_user("toto", "newuser.com"))

	mocks["UserClient"].create_user.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_create(run):
	data, mocks = run(mock_user(*EXISTING_USERS[0].split("@")))

	mocks["UserClient"].create_user.assert_not_called()
	assert data == {"changed": False}
