import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListUsersResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import delete_user
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_USERS = [
	"admin@example.com",
	"admin@example2.com",
]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		delete_user,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.list_users, "return_value", ListUsersResponse(EXISTING_USERS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(username: str, **kwargs):
		return runner_run(params={"username": username}, **kwargs)

	return inner_run


def test_diff_mode_successful_delete(run):
	data, mocks = run(EXISTING_USERS[0], diff=True)

	mocks["UserClient"].delete_user.assert_called_once()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				"admin@example.com",
				"admin@example2.com",
			],
			"after": ["admin@example2.com"],
		},
	}


def test_diff_mode_nothing_to_delete(run):
	data, mocks = run("unknown.com", diff=True)

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				"admin@example.com",
				"admin@example2.com",
			],
			"after": [
				"admin@example.com",
				"admin@example2.com",
			],
		},
	}


def test_check_mode(run):
	data, mocks = run(EXISTING_USERS[0], check_mode=True)

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {"changed": True}


def test_check_mode_nothing_to_delete(run):
	data, mocks = run("admin@unknown.com", check_mode=True)

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {"changed": False}


def test_diff_and_check_modes(run):
	data, mocks = run(EXISTING_USERS[0], check_mode=True, diff=True)

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {
		"changed": True,
		"diff": {
			"before": [
				"admin@example.com",
				"admin@example2.com",
			],
			"after": ["admin@example2.com"],
		},
	}


def test_diff_and_check_modes_nothing_to_delete(run):
	data, mocks = run("unknown.com", check_mode=True, diff=True)

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {
		"changed": False,
		"diff": {
			"before": [
				"admin@example.com",
				"admin@example2.com",
			],
			"after": [
				"admin@example.com",
				"admin@example2.com",
			],
		},
	}


def test_normal_delete(run):
	data, mocks = run(EXISTING_USERS[0])

	mocks["UserClient"].delete_user.assert_called_once()
	assert data == {"changed": True}


def test_normal_nothing_to_delete(run):
	data, mocks = run("unknown.com")

	mocks["UserClient"].delete_user.assert_not_called()
	assert data == {"changed": False}
