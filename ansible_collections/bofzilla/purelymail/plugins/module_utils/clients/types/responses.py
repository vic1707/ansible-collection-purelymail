from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, Json, PositiveFloat
from pydantic.dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule


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

	def dump(self, *, by_alias: bool = False, exclude: set[str] | None = None) -> list[dict[str, Any]]:
		return [r.dump(by_alias=by_alias, exclude=exclude) for r in self.rules]

	def dump_no_id(self, *, by_alias: bool = False) -> list[dict[str, Any]]:
		return [r.dump(by_alias=by_alias, exclude=["id"]) for r in self.rules]

	def filter(self, predicate: Callable[[RoutingRule], bool]) -> "ListRoutingResponse":
		return ListRoutingResponse([r for r in self.rules if predicate(r)])

	def with_added(self, new_rule: RoutingRule) -> "ListRoutingResponse":
		return ListRoutingResponse(self.rules + [new_rule])
