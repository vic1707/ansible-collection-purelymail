from pydantic import ConfigDict, Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class EmptyRequest:
	pass


## Routing
@dataclass(config=ConfigDict(**DEFAULT_CFG))
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

	@model_validator(mode="before")
	@classmethod
	def apply_preset(cls, data: ArgsKwargs) -> ArgsKwargs:
		"""Intercept a 'preset' argument without storing it as a field."""
		match data.kwargs.pop('preset', None):
			case "any_address":
				data.kwargs["match_user"] = ""
				data.kwargs["prefix"] = True
				data.kwargs["catchall"] = False
			case "catchall_except_valid":
				data.kwargs["match_user"] = ""
				data.kwargs["prefix"] = True
				data.kwargs["catchall"] = True
			case "prefix_match":
				data.kwargs["prefix"] = True
				data.kwargs["catchall"] = False
			case "exact_match":
				data.kwargs["prefix"] = False
				data.kwargs["catchall"] = False
		return data


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class DeleteRoutingRequest:
	routingRuleId: int = Field(..., alias="routing_rule_id")
