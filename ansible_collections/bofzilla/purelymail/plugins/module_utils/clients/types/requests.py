from pydantic import ConfigDict, Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import PRESET_MAP, PresetType, RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class EmptyRequest:
	pass


## Routing
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class CreateRoutingRequest(RoutingRule):
	id: None = Field(default=None, init=False, exclude=True)  # doesn't exist yet
	_preset: PresetType | None = Field(default=None, exclude=True, alias="preset")

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
		preset = data.kwargs.get("_preset", None) or data.kwargs.get("preset", None)
		if not preset:
			return data

		normalized_field_names = {f.name: getattr(f.default, "alias", None) or f.name for f in cls.__dataclass_fields__.values()}

		for k, v in PRESET_MAP[preset].items():
			name = normalized_field_names.get(k, k)
			data.kwargs[name] = v
		return data


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class DeleteRoutingRequest:
	routingRuleId: int = Field(..., alias="routing_rule_id")
