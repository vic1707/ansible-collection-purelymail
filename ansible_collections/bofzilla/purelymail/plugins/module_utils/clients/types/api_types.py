from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra="forbid", populate_by_name=True))
class RoutingRule:
	prefix: bool
	catchall: bool
	domainName: str = Field(..., alias="domain_name")
	matchUser: str = Field(..., alias="match_user")
	targetAddresses: list[str] = Field(..., alias="target_addresses")
	id: int = Field(..., gt=0)
