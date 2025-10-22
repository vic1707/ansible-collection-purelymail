from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import (
	PurelymailAPI,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	EmptyRequest,
	DeleteRoutingRequest,
	CreateRoutingRequest
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	EmptyResponse,
	ListRoutingResponse,
)


@dataclass()
class RoutingClient:
	api: PurelymailAPI

	def list_routes(self, req: EmptyRequest = EmptyRequest()) -> ListRoutingResponse:
		return self.api.post("/listRoutingRules", req, ListRoutingResponse)

	def delete_route(self, req: DeleteRoutingRequest) -> EmptyResponse:
		return self.api.post("/deleteRoutingRule", req, EmptyResponse)

	def create_route(self, req: CreateRoutingRequest) -> EmptyResponse:
		return self.api.post("/createRoutingRule", req, EmptyResponse)
