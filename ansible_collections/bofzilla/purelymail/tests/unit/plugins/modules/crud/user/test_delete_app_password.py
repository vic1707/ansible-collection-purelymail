import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import delete_app_password
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(delete_app_password, (("UserClient", lambda _: None),))

	@functools.wraps(runner_run)
	def inner_run(**kwargs):
		return runner_run(params={"user_name": "user@example.com", "app_password": "secret"}, **kwargs)

	return inner_run


def test_normal(run):
	data, mocks = run()

	mocks["UserClient"].delete_app_password.assert_called_once()
	assert data == {"changed": True}


def test_check_mode(run):
	data, mocks = run(check_mode=True)

	mocks["UserClient"].delete_app_password.assert_not_called()
	assert data == {"changed": True}
