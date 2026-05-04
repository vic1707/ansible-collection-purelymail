from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import DeletePasswordResetRequest, ListPasswordResetRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import ListPasswordResetResponse
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: delete_password_reset
short_description: Delete a password reset method for a user
description:
  - Deletes a password reset method for a Purelymail user.
  - When V(target) is omitted, all password reset methods for the user are deleted.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_name:
    description: Full username, e.g. "user@domain.com"
    required: true
    type: str
  target:
    description: Target of the password reset method to delete (email/phone). Omit to delete all methods for the user.
    required: false
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
- name: Delete a specific password reset method
  bofzilla.purelymail.crud.user.delete_password_reset:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
    target: backup@example.com
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
			target=dict(type="str", required=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		user_name = module.params["user_name"]
		target = module.params["target"]

		existing = client.list_password_reset(ListPasswordResetRequest(user_name))

		if target is None:
			# delete-all semantics
			changed = len(existing.users) > 0
			after = ListPasswordResetResponse([])
		else:
			changed = any(m.target == target for m in existing.users)
			after = existing.filter(lambda m: m.target != target)

		result: dict[str, Any] = {"changed": changed}

		if module._diff:
			result["diff"] = {
				"before": existing.as_api_response(),
				"after": after.as_api_response() if changed else existing.as_api_response(),
			}

		if changed and not module.check_mode:
			_ = client.delete_password_reset(DeletePasswordResetRequest(user_name, target))

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
