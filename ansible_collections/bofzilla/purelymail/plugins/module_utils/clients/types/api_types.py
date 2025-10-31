from typing import ClassVar, Literal

from pydantic import ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic.main import IncEx

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

	def dump(self, *, by_alias: bool = False, exclude: IncEx | None = None):
		return RoutingRule._adapter.dump_python(self, by_alias=by_alias, exclude=exclude)

	@property
	def preset(self) -> PresetType | None:
		for preset, values in PRESET_MAP.items():
			if all(getattr(self, field) == expected for field, expected in values.items()):
				return preset
		return None


RoutingRule._adapter = TypeAdapter(RoutingRule)
