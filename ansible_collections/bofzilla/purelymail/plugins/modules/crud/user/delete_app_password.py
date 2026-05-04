from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import DeleteAppPasswordRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: delete_app_password
short_description: Delete an application password for a user
description:
  - Deletes an application password for a Purelymail user.
  - The Purelymail API does not expose a way to list app passwords, so this module always reports changed=true on a successful delete.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_name:
    description: Full username, e.g. "user@domain.com"
    required: true
    type: str
  app_password:
    description: The app password value to delete
    required: true
    type: str

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  idempotent:
    support: none
    details:
      - The Purelymail API does not provide a list endpoint for app passwords, so changed state cannot be reliably inferred.

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Delete an app password
  bofzilla.purelymail.crud.user.delete_app_password:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
    app_password: "{{ lookup('env','APP_PASSWORD') }}"
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
			app_password=dict(type="str", required=True, no_log=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		req = DeleteAppPasswordRequest(
			module.params["user_name"],
			module.params["app_password"],
		)

		result: dict[str, Any] = {"changed": True}

		if not module.check_mode:
			_ = client.delete_app_password(req)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
