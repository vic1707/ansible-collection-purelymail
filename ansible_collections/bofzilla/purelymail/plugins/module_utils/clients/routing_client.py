from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateRoutingRequest, DeleteRoutingRequest, EmptyRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import EmptyResponse, ListRoutingResponse


@dataclass()
class RoutingClient:
	api: PurelymailAPI

	def list_routing_rules(self, req: EmptyRequest = EmptyRequest()) -> ListRoutingResponse:  # noqa: B008
		return self.api.post("/listRoutingRules", req, ListRoutingResponse)

	def delete_routing_rule(self, req: DeleteRoutingRequest) -> EmptyResponse:
		return self.api.post("/deleteRoutingRule", req, EmptyResponse)

	def create_routing_rule(self, req: CreateRoutingRequest) -> EmptyResponse:
		return self.api.post("/createRoutingRule", req, EmptyResponse)
