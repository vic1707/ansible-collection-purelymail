from pydantic import ConfigDict, Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import PRESET_MAP, ApiDomainInfo, PresetType, RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class EmptyRequest:
	pass


## Routing
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class CreateRoutingRequest(RoutingRule):
	id: None = Field(default=None, init=False, exclude=True)  # doesn't exist yet
	_preset: PresetType | None = Field(exclude=True, alias="preset")  # TODO: make default=None when `ty` supports it

	def eq(self, rule: RoutingRule) -> bool:
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
		assert data.args == (), "apply_preset only support kwargs."
		if not data.kwargs:
			return data

		preset = data.kwargs.pop("__preset", None) or data.kwargs.pop("preset", None)
		if preset:
			normalized_names = {f.name: getattr(f.default, "alias", None) or f.name for f in cls.__dataclass_fields__.values()}
			for k, v in PRESET_MAP[preset].items():
				name = normalized_names.get(k, k)
				data.kwargs[name] = v

		data.kwargs["preset"] = None  # TODO: remove when `ty` supports it
		return data


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class DeleteRoutingRequest:
	routingRuleId: int = Field(..., alias="routing_rule_id")


## Domain
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class AddDomainRequest:
	domainName: str = Field(..., alias="domain_name")


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ListDomainsRequest:
	includeShared: bool = Field(default=False, alias="include_shared")  # TODO: default?


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class UpdateDomainSettingsRequest:
	name: str
	allowAccountReset: bool | None = Field(default=None, alias="allow_account_reset")
	symbolicSubaddressing: bool | None = Field(default=None, alias="symbolic_subaddressing")
	recheckDns: bool = Field(default=False, alias="recheck_dns")

	def updates(self, domain: ApiDomainInfo) -> bool:
		return (
			self.recheckDns  # assume changes so we request
			or (self.allowAccountReset is not None and self.allowAccountReset != domain.allowAccountReset)
			or (self.symbolicSubaddressing is not None and self.symbolicSubaddressing != domain.symbolicSubaddressing)
		)

	def update(self, domain: ApiDomainInfo) -> ApiDomainInfo:
		return ApiDomainInfo(
			name=domain.name,
			allowAccountReset=(self.allowAccountReset if self.allowAccountReset is not None else domain.allowAccountReset),
			symbolicSubaddressing=(self.symbolicSubaddressing if self.symbolicSubaddressing is not None else domain.symbolicSubaddressing),
			isShared=domain.isShared,
			dnsSummary=domain.dnsSummary,
		)


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class DeleteDomainRequest:
	name: str
