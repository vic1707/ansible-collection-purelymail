from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import GetUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: get_user
short_description: Get user details from Purelymail
description:
  - Gets user details and configuration.
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
  diff_mode:
    support: full

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Get user details
  bofzilla.purelymail.crud.user.get_user:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
"""

RETURN = r"""
user:
  description: User details from API
  returned: success
  type: dict
  contains:
    enableSearchIndexing:
      description: Whether search indexing is enabled for this user
      type: bool
    recoveryEnabled:
      description: Whether password recovery is enabled for this user
      type: bool
    requireTwoFactorAuthentication:
      description: Whether this user requires 2FA for login
      type: bool
    enableSpamFiltering:
      description: Whether spam filtering is enabled for this user
      type: bool
    resetMethods:
      description: List of password reset methods available for this user
      type: list
      elements: dict
      contains:
        type:
          description: Type of reset method
          type: str
        target:
          description: Target of the reset method (e.g., email address)
          type: str
        description:
          description: Description of the reset method
          type: str
        allowMfaReset:
          description: Whether MFA reset is allowed via this method
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
		name = module.params["user_name"]
		user = client.get_user(GetUserRequest(name)).as_api_response()
		result: dict[str, Any] = {"changed": False, "user": user}

		if module._diff:
			result["diff"] = {"before": user, "after": user}

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
