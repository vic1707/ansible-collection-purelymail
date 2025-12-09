import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListUsersResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import list_users
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401

EXISTING_USERS = ["admin@example.com"]


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		list_users,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.list_users, "return_value", ListUsersResponse(EXISTING_USERS)),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(**kwargs):
		# include_shared doesn't matter as we don't test purelymail's API
		# only this module behaviors
		return runner_run(params={"include_shared": True}, **kwargs)

	return inner_run


def test_diff(run):
	data, _ = run(diff=True)

	assert data == {
		"changed": False,
		"users": ["admin@example.com"],
		"diff": {
			"before": ["admin@example.com"],
			"after": ["admin@example.com"],
		},
	}


def test_check(run):
	data, _ = run(check_mode=True)

	assert data == {"changed": False}


def test_check_and_diff(run):
	data, _ = run(check_mode=True, diff=True)

	assert data == {
		"changed": False,
		"diff": {
			"before": ["admin@example.com"],
			"after": ["admin@example.com"],
		},
	}


def test_normal_nonshared(run):
	data, _ = run()

	assert data == {
		"changed": False,
		"users": ["admin@example.com"],
	}


def test_normal(run):
	data, _ = run()

	assert data == {
		"changed": False,
		"users": ["admin@example.com"],
	}
