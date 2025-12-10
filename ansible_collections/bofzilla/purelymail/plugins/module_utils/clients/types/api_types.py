from typing import ClassVar, Literal

from pydantic import ConfigDict, Field, TypeAdapter, computed_field
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG

PresetType = Literal["any_address", "catchall_except_valid", "prefix_match", "exact_match"]
PRESET_MAP: dict[PresetType, dict] = {
	"any_address": {"matchUser": "", "prefix": True, "catchall": False},
	"catchall_except_valid": {"matchUser": "", "prefix": True, "catchall": True},
	"prefix_match": {"prefix": True, "catchall": False},
	"exact_match": {"prefix": False, "catchall": False},
}


@dataclass(config=ConfigDict(**DEFAULT_CFG, validate_by_name=True, validate_by_alias=True))
class RoutingRule:
	_adapter: ClassVar[TypeAdapter["RoutingRule"]]

	prefix: bool
	catchall: bool
	domainName: str = Field(..., alias="domain_name")
	matchUser: str = Field(..., alias="match_user")
	targetAddresses: list[str] = Field(..., alias="target_addresses")
	id: int = Field(..., gt=0)

	def as_display(self):
		return RoutingRule._adapter.dump_python(self, exclude={"id"})

	def as_api_response(self):
		return RoutingRule._adapter.dump_python(self, exclude={"preset"})

	def as_api_payload(self):
		return RoutingRule._adapter.dump_python(self, exclude={"preset", "id"})

	def as_playbook_input(self):
		return RoutingRule._adapter.dump_python(self, by_alias=True, exclude={"preset", "id"})

	@computed_field(return_type=PresetType | None)
	@property
	def preset(self) -> PresetType | None:
		for preset, values in PRESET_MAP.items():
			if all(getattr(self, field) == expected for field, expected in values.items()):
				return preset
		return None


RoutingRule._adapter = TypeAdapter(RoutingRule)


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ApiDomainDnsSummary:
	passesMx: bool
	passesSpf: bool
	passesDkim: bool
	passesDmarc: bool


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ApiDomainInfo:
	_adapter: ClassVar[TypeAdapter["ApiDomainInfo"]]

	name: str
	allowAccountReset: bool
	symbolicSubaddressing: bool
	isShared: bool
	dnsSummary: ApiDomainDnsSummary

	def as_api_response(self):
		return ApiDomainInfo._adapter.dump_python(self)

	def as_display(self):
		return ApiDomainInfo._adapter.dump_python(self)

	def DEFAULT(domain_name: str) -> "ApiDomainInfo":
		"""
		AddDomain doesn't return anything, but accepted domains should return this.
		*Note*: dnsSummary is all True because else the create call would fail.
		"""
		return ApiDomainInfo(
			name=domain_name,
			allowAccountReset=True,
			symbolicSubaddressing=True,
			isShared=False,
			dnsSummary=ApiDomainDnsSummary(True, True, True, True),
		)


ApiDomainInfo._adapter = TypeAdapter(ApiDomainInfo)


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class UserPasswordResetMethodType:
	pass


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class GetUserPasswordResetMethod:
	type: UserPasswordResetMethodType
	target: str
	description: str
	allowMfaReset: bool
