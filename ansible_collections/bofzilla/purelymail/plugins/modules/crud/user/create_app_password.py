from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateAppPasswordRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: create_app_password
short_description: Create an application password for a user
description:
  - Creates a new application password for a Purelymail user.
  - The Purelymail API does not expose a way to list app passwords, so this module is not idempotent;
    every successful run creates a new app password.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_handle:
    description: Full user handle, e.g. "user@domain.com"
    required: true
    type: str
  name:
    description: Optional user-friendly description of the app password
    required: false
    type: str
    default: ""

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  idempotent:
    support: none
    details:
      - The Purelymail API does not provide a list endpoint for app passwords, so each invocation creates a new password.

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Create an app password
  bofzilla.purelymail.crud.user.create_app_password:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_handle: user@example.com
    name: my-mail-client
  register: app_pw

- name: Show generated password
  ansible.builtin.debug:
    var: app_pw.app_password
"""

RETURN = r"""
app_password:
  description: The generated app password. Returned only when not running in check mode.
  returned: success
  type: str
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_handle=dict(type="str", required=True),
			name=dict(type="str", required=False, default=""),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		req = CreateAppPasswordRequest(module.params["user_handle"], module.params["name"])

		result: dict[str, Any] = {"changed": True}

		if not module.check_mode:
			resp = client.create_app_password(req)
			result["app_password"] = resp.appPassword

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
