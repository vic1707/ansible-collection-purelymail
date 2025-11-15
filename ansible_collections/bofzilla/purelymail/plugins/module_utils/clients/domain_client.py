from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	AddDomainRequest,
	DeleteDomainRequest,
	EmptyRequest,
	ListDomainsRequest,
	UpdateDomainSettingsRequest,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	EmptyResponse,
	GetOwnershipCodeResponse,
	ListDomainsResponse,
)


@dataclass()
class DomainClient:
	api: PurelymailAPI

	def add_domain(self, req: AddDomainRequest) -> EmptyResponse:
		return self.api.post("/addDomain", req, EmptyResponse)

	def get_ownership_code(self, req: EmptyRequest = EmptyRequest()) -> GetOwnershipCodeResponse:  # noqa: B008
		return self.api.post("/getOwnershipCode", req, GetOwnershipCodeResponse)

	def list_domains(self, req: ListDomainsRequest) -> ListDomainsResponse:
		res = self.api.post("/listDomains", req, ListDomainsResponse)
		assert req.includeShared or all(not d.isShared for d in res.domains), (
			f"[Purelymail error]: API returned shared domains despite includeShared=False ({[d.name for d in res.domains if d.isShared]})"
		)
		return res

	def update_domain_settings(self, req: UpdateDomainSettingsRequest) -> EmptyResponse:
		return self.api.post("/updateDomainSettings", req, EmptyResponse)

	def delete_domain(self, req: DeleteDomainRequest) -> EmptyResponse:
		return self.api.post("/deleteDomain", req, EmptyResponse)
