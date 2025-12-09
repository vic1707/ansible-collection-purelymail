from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: list_users
short_description: List existing users on Purelymail account
description:
  - Connects to the Purelymail API and returns the list of existing users.
options:
  api_token:
    description: Purelymail API token
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
- name: List accessible users
  bofzilla.purelymail.crud.user.list_users:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
users:
  description: List of users existing on the account
  type: list
  elements: str
  returned: success
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			include_shared=dict(type="bool", required=False, default=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		users = client.list_users().users

		res = {"changed": False}

		if module._diff:
			res["diff"] = {"before": users, "after": users}

		if not module.check_mode:
			res["users"] = users

		module.exit_json(**res)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
