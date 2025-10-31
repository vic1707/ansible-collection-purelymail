from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, Json, PositiveFloat
from pydantic.dataclasses import dataclass
from pydantic.main import IncEx

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import RoutingRule
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

	def dump(self, *, by_alias: bool = False, exclude: IncEx | None = None) -> list[dict[str, Any]]:
		return [r.dump(by_alias=by_alias, exclude=exclude) for r in self.rules]

	def dump_no_id(self, *, by_alias: bool = False) -> list[dict[str, Any]]:
		return [r.dump(by_alias=by_alias, exclude=["id"]) for r in self.rules]

	def filter(self, predicate: Callable[[RoutingRule], bool]) -> "ListRoutingResponse":
		"""True means keep"""
		return ListRoutingResponse([r for r in self.rules if predicate(r)])

	def concat(self, new_rules: list[RoutingRule]) -> "ListRoutingResponse":
		return ListRoutingResponse(self.rules + new_rules)
