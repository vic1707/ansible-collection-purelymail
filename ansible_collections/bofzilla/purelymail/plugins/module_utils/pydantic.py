from pydantic import ConfigDict

DEFAULT_CFG = ConfigDict(
	extra="forbid",
	frozen=True,
	strict=True,
	validate_default=True,
	validate_return=True,
)
