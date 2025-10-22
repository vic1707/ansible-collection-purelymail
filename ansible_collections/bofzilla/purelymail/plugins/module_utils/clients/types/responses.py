from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing import List

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import (
	RoutingRule,
)

@dataclass(config=ConfigDict(extra="forbid"))
class EmptyResponse:
	pass

## Billing
@dataclass(config=ConfigDict(extra="forbid"))
class CheckCreditResponse:
	credit: str


## Routing
@dataclass(config=ConfigDict(extra="forbid"))
class ListRoutingResponse:
	rules: List[RoutingRule]
