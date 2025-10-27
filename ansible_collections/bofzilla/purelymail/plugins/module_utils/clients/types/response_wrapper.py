from typing import Annotated, Literal, TypeVar

from pydantic import ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass

T = TypeVar("T")


@dataclass(config=ConfigDict(extra="forbid"))
class ApiSuccess[T]:
	type: Literal["success"]
	result: T


@dataclass(config=ConfigDict(extra="forbid"))
class ApiError(Exception):
	type: Literal["error"]
	code: str
	message: str

	def __str__(self):
		return f"[{self.code}] {self.message}"


type ApiResponse[T] = Annotated[ApiSuccess[T] | ApiError, Field(..., discriminator="type")]


def parse_api_response(data: dict) -> ApiSuccess[T] | ApiError:
	return TypeAdapter(ApiResponse[T]).validate_python(data, extra="forbid")
