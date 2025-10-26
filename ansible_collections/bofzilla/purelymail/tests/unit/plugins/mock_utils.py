from types import ModuleType
from unittest.mock import MagicMock

from pytest import MonkeyPatch


# Mapped type like in TS would be cleaner
def bootstrap_module(
	monkeypatch: MonkeyPatch,
	py_module: ModuleType,
	mocks: tuple[str, ...] = (),
) -> dict[str, MagicMock]:
	module = MagicMock()
	module.exit_json.side_effect = exit_json
	module.fail_json.side_effect = fail_json
	monkeypatch.setattr(py_module, "AnsibleModule", lambda *_, **__: module)

	ret = {"AnsibleModule": module}

	for mock_name in mocks:
		mock = MagicMock()
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
