from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import ConfigDict, Field, Json, PositiveFloat, TypeAdapter, computed_field
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainInfo, GetUserPasswordResetMethod, RoutingRule
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import UpdateDomainSettingsRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class EmptyResponse:
	pass


## Billing
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class CheckCreditResponse:
	credit: Json[PositiveFloat]


## Routing
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ListRoutingResponse:
	rules: list[RoutingRule]

	def as_api_payloads(self) -> list[dict[str, Any]]:
		return [r.as_api_payload() for r in self.rules]

	def as_api_response(self) -> list[dict[str, Any]]:
		return [r.as_api_response() for r in self.rules]

	def as_display(self) -> list[dict[str, Any]]:
		return [r.as_display() for r in self.rules]

	def filter(self, predicate: Callable[[RoutingRule], bool]) -> "ListRoutingResponse":
		"""True means keep"""
		return ListRoutingResponse([r for r in self.rules if predicate(r)])

	def concat(self, new_rules: list[RoutingRule]) -> "ListRoutingResponse":
		return ListRoutingResponse(self.rules + new_rules)


## Domain
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class GetOwnershipCodeResponse:
	code: str = Field(..., pattern=r"^purelymail_ownership_proof=[A-Za-z0-9]+$")

	@computed_field(return_type=str)
	@property
	def value(self) -> str:
		return self.code.split("=")[1]


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ListDomainsResponse:
	domains: list[ApiDomainInfo]

	def as_api_response(self) -> list[dict[str, Any]]:
		return [r.as_api_response() for r in self.domains]

	def as_display(self) -> list[dict[str, Any]]:
		return [r.as_display() for r in self.domains]

	def filter(self, predicate: Callable[[ApiDomainInfo], bool]) -> "ListDomainsResponse":
		"""True means keep"""
		return ListDomainsResponse([d for d in self.domains if predicate(d)])

	def concat(self, new_domains: list[ApiDomainInfo]) -> "ListDomainsResponse":
		return ListDomainsResponse(self.domains + new_domains)

	def apply_updates(self, updates: list[UpdateDomainSettingsRequest]) -> "ListDomainsResponse":
		update_map = {u.name: u for u in updates}

		return ListDomainsResponse([update_map[d.name].update(d) if d.name in update_map else d for d in self.domains])


## User
@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ListUsersResponse:
	users: list[str]

	def as_api_response(self) -> list[str]:
		return [u for u in self.users]

	def filter(self, predicate: Callable[[str], bool]) -> "ListUsersResponse":
		"""True means keep"""
		return ListUsersResponse([u for u in self.users if predicate(u)])

	def concat(self, new_users: list[str]) -> "ListUsersResponse":
		return ListUsersResponse(self.users + new_users)


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class GetUserResponse:
	_adapter: ClassVar[TypeAdapter["GetUserResponse"]]

	enableSearchIndexing: bool
	recoveryEnabled: bool
	requireTwoFactorAuthentication: bool
	enableSpamFiltering: bool
	resetMethods: list[GetUserPasswordResetMethod]

	def as_api_response(self) -> dict:
		return GetUserResponse._adapter.dump_python(self)


GetUserResponse._adapter = TypeAdapter(GetUserResponse)
