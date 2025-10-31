from typing import ClassVar

from pydantic import ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic.main import IncEx

from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG, populate_by_name=True))
class RoutingRule:
	_adapter: ClassVar[TypeAdapter["RoutingRule"]]

	prefix: bool
	catchall: bool
	domainName: str = Field(..., alias="domain_name")
	matchUser: str = Field(..., alias="match_user")
	targetAddresses: list[str] = Field(..., alias="target_addresses")
	id: int = Field(..., gt=0)

	def dump(self, *, by_alias: bool = False, exclude: IncEx | None = None):
		return RoutingRule._adapter.dump_python(self, by_alias=by_alias, exclude=exclude)


RoutingRule._adapter = TypeAdapter(RoutingRule)
