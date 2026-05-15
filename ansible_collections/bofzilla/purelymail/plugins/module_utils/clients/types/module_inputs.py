from typing import Annotated

from pydantic import BeforeValidator, ConfigDict, Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.pydantic import DEFAULT_CFG


@dataclass(config=ConfigDict(**DEFAULT_CFG, validate_by_name=True, validate_by_alias=True))
class UserInput(CreateUserRequest):
	password: Annotated[str, BeforeValidator(lambda value: value or "")] = Field(default="", alias="password")
	passwordMode: str | None = Field(default=None, alias="password_mode", exclude=True)
	requireTwoFactorAuthentication: bool = Field(default=False, alias="require_two_factor_authentication", exclude=True)
	recoveryEmailAllowMfaReset: bool = Field(default=True, alias="recovery_email_allow_mfa_reset", exclude=True)
	recoveryPhoneAllowMfaReset: bool = Field(default=True, alias="recovery_phone_allow_mfa_reset", exclude=True)

	@model_validator(mode="before")
	@classmethod
	def split_name(cls, data: ArgsKwargs) -> ArgsKwargs:
		if not data.kwargs:  # pragma: no cover
			return data
		if email := data.kwargs.pop("name", None):
			data.kwargs["user_name"], data.kwargs["domain_name"] = email.rsplit("@", 1)
		return data
