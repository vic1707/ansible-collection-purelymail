from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: create_user
short_description: Create a new user
description:
  - This module connects to Purelymail API and creates a new user
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  user_name:
    required: true
    type: str
  domain_name:
    required: true
    type: str
  password:
    required: true
    type: str
  enable_password_reset:
    required: true
    type: bool
  recovery_email:
    required: true
    type: str
  recovery_email_description:
    required: true
    type: str
  recovery_phone:
    required: true
    type: str
  recovery_phone_description:
    required: true
    type: str
  enable_search_indexing:
    required: true
    type: bool
  send_welcome_email:
    required: true
    type: bool

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
- name: Create a new user
  bofzilla.purelymail.crud.domain.create_user:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    domain_name: example.com
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
			domain_name=dict(type="str", required=True),
			password=dict(type="str", required=True, no_log=True),
			enable_password_reset=dict(type="bool", required=True),
			recovery_email=dict(type="str", required=True),
			recovery_email_description=dict(type="str", required=True),
			recovery_phone=dict(type="str", required=True),
			recovery_phone_description=dict(type="str", required=True),
			enable_search_indexing=dict(type="bool", required=True),
			send_welcome_email=dict(type="bool", required=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		user_spec = module.params
		del user_spec["api_token"]
		user = CreateUserRequest(**user_spec)

		existing_users = client.list_users()

		result = {"changed": user.email not in existing_users.users}

		if module._diff:
			result["diff"] = {
				"before": existing_users.as_api_response(),
				"after": existing_users.concat([user.email]).as_api_response() if result["changed"] else existing_users.as_api_response(),
			}

		if result["changed"] and not module.check_mode:
			_ = client.create_user(user)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
