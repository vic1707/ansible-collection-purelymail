from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra="forbid"))
class EmptyResponse:
	pass

## Billing
@dataclass(config=ConfigDict(extra="forbid"))
class CheckCreditResponse:
	credit: str
