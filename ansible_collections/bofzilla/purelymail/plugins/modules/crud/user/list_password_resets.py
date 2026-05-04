from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import ListPasswordResetRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: list_password_resets
short_description: List password reset methods of a user
description:
  - Connects to the Purelymail API and returns the list of password reset methods of a user.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_name:
    description: Full username, e.g. "user@domain.com"
    required: true
    type: str

attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: full
    details:
      - This action does not modify state.
  idempotent:
    support: full
    details:
      - This action does not modify state.

author:
  - vic1707
"""

EXAMPLES = r"""
- name: List password reset methods for a user
  bofzilla.purelymail.crud.user.list_password_resets:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
"""

RETURN = r"""
methods:
  description: List of password reset methods configured for the user
  returned: success
  type: list
  elements: dict
  contains:
    type:
      description: Type of reset method (e.g. "email", "phone")
      type: str
    target:
      description: Target of the reset method (e.g. email address)
      type: str
    description:
      description: Human-readable description
      type: str
    allowMfaReset:
      description: Whether this method allows MFA reset
      type: bool
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		methods = client.list_password_reset(ListPasswordResetRequest(module.params["user_name"])).as_api_response()

		result: dict[str, Any] = {"changed": False, "methods": methods}

		if module._diff:
			result["diff"] = {"before": methods, "after": methods}

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
