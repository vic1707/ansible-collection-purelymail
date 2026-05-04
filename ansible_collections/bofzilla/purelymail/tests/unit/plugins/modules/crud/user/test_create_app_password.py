import functools

import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import CreateAppPasswordResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.user import create_app_password
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	runner_run = make_runner(
		create_app_password,
		(
			(
				"UserClient",
				lambda mock: setattr(mock.create_app_password, "return_value", CreateAppPasswordResponse(appPassword="generated-pw")),
			),
		),
	)

	@functools.wraps(runner_run)
	def inner_run(params: dict | None = None, **kwargs):
		params = params or {}
		params.setdefault("user_handle", "user@example.com")
		params.setdefault("name", "")
		return runner_run(params=params, **kwargs)

	return inner_run


def test_normal(run):
	data, mocks = run()

	mocks["UserClient"].create_app_password.assert_called_once()
	assert data == {"changed": True, "app_password": "generated-pw"}


def test_with_name(run):
	data, mocks = run({"name": "my-client"})

	mocks["UserClient"].create_app_password.assert_called_once()
	assert data == {"changed": True, "app_password": "generated-pw"}


def test_check_mode(run):
	data, mocks = run(check_mode=True)

	mocks["UserClient"].create_app_password.assert_not_called()
	assert data == {"changed": True}
