from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule


@dataclass(config=ConfigDict(extra="forbid"))
class EmptyRequest:
	pass


## Routing
@dataclass(config=ConfigDict(extra="forbid"))
class CreateRoutingRequest(RoutingRule):
	id: None = Field(default=None, init=False)  # doesn't exist yet

	def matches(self, rule: RoutingRule) -> bool:
		return (
			self.prefix == rule.prefix
			and self.catchall == rule.catchall
			and self.domainName == rule.domainName
			and self.matchUser == rule.matchUser
			and self.targetAddresses == rule.targetAddresses
		)


@dataclass(config=ConfigDict(extra="forbid"))
class DeleteRoutingRequest:
	routingRuleId: int = Field(..., alias="routing_rule_id")
