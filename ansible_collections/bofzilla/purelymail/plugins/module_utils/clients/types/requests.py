from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from pydantic import Field

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import (
	RoutingRule,
)


@dataclass(config=ConfigDict(extra="forbid"))
class EmptyRequest:
	pass


## Routing
@dataclass(config=ConfigDict(extra="forbid"))
class CreateRoutingRequest(RoutingRule):
	id: None = Field(default=None, init=False)  # doesn't exist yet
	catchall: bool = False


@dataclass(config=ConfigDict(extra="forbid"))
class DeleteRoutingRequest:
	routingRuleId: int = Field(..., alias="routing_rule_id")
