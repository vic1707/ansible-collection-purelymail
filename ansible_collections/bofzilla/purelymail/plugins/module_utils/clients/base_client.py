import os
from dataclasses import dataclass, field
from typing import TypeVar

import requests
from pydantic import TypeAdapter

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiSuccess, parse_api_response

Rep = TypeVar("Rep")
Req = TypeVar("Req")


def _default_tls_verify() -> bool:
	return os.environ.get("PURELYMAIL_API_TLS_VERIFY", "true") == "true"


@dataclass()
class PurelymailAPI:
	api_token: str
	base_url: str = "https://purelymail.com/api"
	api_version: str = "v0"
	tls_verify: bool = field(default_factory=_default_tls_verify)

	@property
	def url(self):
		return f"{self.base_url}/{self.api_version}"

	def post(self, endpoint: str, payload: Req, response_model: type[Rep]) -> Rep:
		# Use pydantic to serialize: respects Field(exclude=...), recurses into
		# nested dataclasses, and emits field names (which match the API's
		# camelCase contract — aliases are for input only).
		body = TypeAdapter(type(payload)).dump_python(payload, mode="json")

		resp = requests.post(
			f"{self.url}/{endpoint.lstrip('/')}",
			headers={"Purelymail-Api-Token": self.api_token},
			json=body,
			verify=self.tls_verify,
		)

		# Parse the body first: the Purelymail API can return structured errors
		# under non-2xx as well as 200 OK, and we want the typed ApiError instead
		# of a bare HTTPError when possible.
		try:
			payload_json = resp.json()
		except ValueError:
			resp.raise_for_status()
			raise  # pragma: no cover  # response wasn't JSON but was 2xx

		data = parse_api_response(payload_json, response_model)
		match data:
			case ApiSuccess():
				return data.result
			case err:
				raise err
