from typing import Any

from pydantic import ConfigDict, Json, PositiveFloat
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import (
	RoutingRule,
)


@dataclass(config=ConfigDict(extra="forbid"))
class EmptyResponse:
	pass


## Billing
@dataclass(config=ConfigDict(extra="forbid"))
class CheckCreditResponse:
	credit: Json[PositiveFloat]


## Routing
@dataclass(config=ConfigDict(extra="forbid"))
class ListRoutingResponse:
	rules: list[RoutingRule]

	def as_dict(self) -> list[dict[str, Any]]:
		return [r.__dict__ for r in self.rules]

	def filter(self, predicate):
		return ListRoutingResponse([r for r in self.rules if predicate(r)])
