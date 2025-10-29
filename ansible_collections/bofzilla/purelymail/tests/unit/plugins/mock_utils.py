import functools
from collections.abc import Callable
from typing import Any, Protocol
from unittest.mock import MagicMock

import pytest


@pytest.fixture(scope="module")
def make_runner():
	"""
	Returns a factory that can produce a `run()` callable for any Ansible module.
	"""

	def _make_runner(
		py_module: HasMain,
		mock_setup: tuple[tuple[str, Callable[[MagicMock], None]] | str, ...],
	) -> Callable[..., tuple[dict, dict[str, MagicMock]]]:
		monkeypatch = pytest.MonkeyPatch()
		mocks = bootstrap_module(monkeypatch, py_module, mocks=mock_setup)

		@functools.wraps(run_module_test)
		def run_with_params(**kwargs):
			return run_module_test(py_module, mocks, **kwargs)

		return run_with_params

	return _make_runner


class HasMain(Protocol):
	def main(self) -> None: ...


# Mapped type like in TS would be cleaner
def bootstrap_module(
	monkeypatch: pytest.MonkeyPatch,
	py_module: HasMain,
	mocks: tuple[tuple[str, Callable[[MagicMock], None]] | str, ...] = (),
) -> dict[str, MagicMock]:
	module = MagicMock()
	module.exit_json.side_effect = exit_json
	module.fail_json.side_effect = fail_json
	monkeypatch.setattr(py_module, "AnsibleModule", lambda *_, **__: module)

	ret = {"AnsibleModule": module}

	for mock_cfg in mocks:
		mock = MagicMock()
		if isinstance(mock_cfg, tuple):
			mock_name = mock_cfg[0]
			mock_cfg[1](mock)
		else:
			mock_name = mock_cfg

		monkeypatch.setattr(py_module, mock_name, lambda *_, __mock=mock, **__: __mock)
		ret[mock_name] = mock

	return ret


class AnsibleExitJson(BaseException):
	pass


class AnsibleFailJson(BaseException):
	pass


def exit_json(*_, **kwargs):
	raise AnsibleExitJson(kwargs)


def fail_json(*_, **kwargs):
	raise AnsibleFailJson(kwargs)


def run_module_test(
	py_module: HasMain,
	mocks: dict[str, MagicMock],
	*,
	params: dict[str, Any] | None = None,
	diff: bool = False,
	check_mode: bool = False,
	expect: type[BaseException | Exception] = AnsibleExitJson,
) -> tuple[Any, dict[str, MagicMock]]:
	module = mocks["AnsibleModule"]
	module._diff = diff
	module.check_mode = check_mode
	module.params = {"api_token": "dQw4w9WgXcQ", **(params or {})}

	with pytest.raises(expect) as excinfo:
		py_module.main()

	return excinfo.value.args[0], mocks
