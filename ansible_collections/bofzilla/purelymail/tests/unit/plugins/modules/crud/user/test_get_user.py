import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import get_user
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import AnsibleFailJson, FakeApiResponse, make_runner  # noqa: F401

EXISTING_USERS = {
	"existing@example.com": FakeApiResponse.success(
		{"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []}
	)
}


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		get_user,
		(),
		lambda payload: EXISTING_USERS.get(payload["userName"], FakeApiResponse.error(f"Unknown user {payload['userName']}")),
	)

	@functools.wraps(runner_run)
	def inner_run(username: str, **kwargs):
		return runner_run(params={"username": username}, **kwargs)

	return inner_run


def test_diff_mode(run):
	data, _ = run("existing@example.com", diff=True)

	assert data == {
		"changed": False,
		"diff": {
			"before": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
			"after": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
		},
		"user": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
	}


def test_diff_mode_unknown(run):
	data, _ = run("admin@unknown.com", diff=True, expect=AnsibleFailJson)

	assert data["msg"] == "Purelymail API error: [internalError] Unknown user admin@unknown.com"


def test_check_mode(run):
	data, _ = run("existing@example.com", check_mode=True)

	assert data == {"changed": False}


def test_check_mode_unknown(run):
	data, _ = run("admin@unknown.com", check_mode=True, expect=AnsibleFailJson)

	assert data["msg"] == "Purelymail API error: [internalError] Unknown user admin@unknown.com"


def test_diff_and_check_modes(run):
	data, mocks = run("existing@example.com", check_mode=True, diff=True)

	assert data == {
		"changed": False,
		"diff": {
			"before": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
			"after": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
		},
	}


def test_diff_and_check_modes_unknown(run):
	data, _ = run("admin@unknown.com", check_mode=True, diff=True, expect=AnsibleFailJson)

	assert data["msg"] == "Purelymail API error: [internalError] Unknown user admin@unknown.com"


def test_normal(run):
	data, _ = run("existing@example.com")

	assert data == {
		"changed": False,
		"user": {"enableSearchIndexing": True, "enableSpamFiltering": True, "recoveryEnabled": False, "requireTwoFactorAuthentication": False, "resetMethods": []},
	}


def test_normal_unknown(run):
	data, _ = run("admin@unknown.com", expect=AnsibleFailJson)

	assert data["msg"] == "Purelymail API error: [internalError] Unknown user admin@unknown.com"
