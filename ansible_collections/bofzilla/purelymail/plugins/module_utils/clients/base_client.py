import os
from dataclasses import dataclass
from typing import TypeVar

import requests
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import (
	ApiError,
	ApiSuccess,
	parse_api_response,
)

Rep = TypeVar("Rep")
Req = TypeVar("Req")


@dataclass()
class PurelymailAPI:
	__module: AnsibleModule
	api_token: str
	base_url: str = "https://purelymail.com/api"
	api_version: str = "v0"
	TLS_VERIFY = os.environ.get("PURELYMAIL_API_TLS_VERIFY", "true") == "true"

	@property
	def url(self):
		return f"{self.base_url}/{self.api_version}"

	def post(self, endpoint: str, payload: Req, response_model: type[Rep]) -> Rep:
		resp = requests.post(
			f"{self.url}/{endpoint.lstrip('/')}",
			headers={"Purelymail-Api-Token": self.api_token},
			json=payload.__dict__,
			verify=self.TLS_VERIFY,
		)
		resp.raise_for_status()

		data = parse_api_response(resp.json())
		match data:
			case ApiSuccess():
				return response_model(**data.result)
			case ApiError():
				return self.__module.fail_json("Purelymail API error", exception=data)
			case other:
				raise ValueError(f"Unexpected response type: {other}")
