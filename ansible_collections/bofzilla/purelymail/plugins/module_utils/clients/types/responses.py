from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, Field, Json, PositiveFloat
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainInfo, RoutingRule
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


@dataclass(config=ConfigDict(**DEFAULT_CFG))
class ListDomainsResponse:
	domains: list[ApiDomainInfo]

	def as_api_response(self) -> list[dict[str, Any]]:
		return [r.as_api_response() for r in self.domains]
