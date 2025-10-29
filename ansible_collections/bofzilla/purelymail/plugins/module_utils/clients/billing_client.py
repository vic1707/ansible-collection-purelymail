from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import EmptyRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import CheckCreditResponse


@dataclass()
class BillingClient:
	api: PurelymailAPI

	def check_account_credit(self, req: EmptyRequest = EmptyRequest()) -> CheckCreditResponse:  # noqa: B008
		return self.api.post("/checkAccountCredit", req, CheckCreditResponse)
