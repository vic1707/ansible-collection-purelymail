from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import DeleteUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: delete_user
short_description: Delete a user from Purelymail
description:
  - Deletes a user and all related configuration and users.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  username:
    description: The name of the user to delete
    required: true
    type: str

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  idempotent:
    support: full

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Delete a user
  bofzilla.purelymail.crud.user.delete_user:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    username: example.com
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			username=dict(type="str", required=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		name = module.params["username"]
		existing_users = client.list_users()

		exists = any(u == name for u in existing_users.users)
		result = {"changed": exists}

		if module._diff:
			result["diff"] = {
				"before": existing_users.as_api_response(),
				"after": existing_users.filter(lambda u: u != name).as_api_response() if exists else existing_users.as_api_response(),
			}

		if exists and not module.check_mode:
			_ = client.delete_user(DeleteUserRequest(name))

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
