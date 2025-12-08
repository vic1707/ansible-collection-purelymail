import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import CheckCreditResponse
from ansible_collections.bofzilla.purelymail.plugins.modules.crud.billing import check_credit_info
from ansible_collections.bofzilla.purelymail.tests.unit.plugins.mock_utils import make_runner  # noqa: F401


@pytest.fixture(scope="module")
def run(make_runner):  # noqa: F811
	return make_runner(
		check_credit_info,
		(
			(
				"BillingClient",
				lambda mock: setattr(mock.check_account_credit, "return_value", CheckCreditResponse("12.34")),  # TODO: # ty:ignore[invalid-argument-type]
			),
		),
	)


def test_diff(run):
	data, _ = run(diff=True)
	assert data == {
		"changed": False,
		"credit": 12.34,
		"diff": {"before": {"credit": 12.34}, "after": {"credit": 12.34}},
	}


def test_check(run):
	data, _ = run(check_mode=True)
	assert data == {"changed": False}


def test_check_and_diff(run):
	data, _ = run(diff=True, check_mode=True)
	assert data == {
		"changed": False,
		"diff": {"before": {"credit": 12.34}, "after": {"credit": 12.34}},
	}


def test_normal(run):
	data, _ = run()
	assert data == {"changed": False, "credit": 12.34}
