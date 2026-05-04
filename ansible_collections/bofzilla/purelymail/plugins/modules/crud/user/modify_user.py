from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import GetUserRequest, ModifyUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: modify_user
short_description: Modify an existing user
description:
  - Modifies attributes of an existing Purelymail user.
  - Only fields that are provided are sent to the API.
  - Idempotency for V(new_password) cannot be determined; the module will always
    report a change when V(new_password) is given. All other fields are checked
    against the current state.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_name:
    description: Full username, e.g. "user@domain.com"
    required: true
    type: str
  new_user_name:
    description: New full username for the user
    required: false
    type: str
  new_password:
    description: New password for the user. Idempotency cannot be checked.
    required: false
    type: str
  enable_search_indexing:
    description: Whether search indexing should be enabled for this user
    required: false
    type: bool
  enable_password_reset:
    description: Whether this user can have their password reset
    required: false
    type: bool
  require_two_factor_authentication:
    description: Whether this user requires 2FA for login
    required: false
    type: bool

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  idempotent:
    support: partial
    details:
      - V(new_password) cannot be compared with current state, so the module always reports changed when it is provided.

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Disable search indexing for a user
  bofzilla.purelymail.crud.user.modify_user:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
    enable_search_indexing: false
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
			new_user_name=dict(type="str", required=False),
			new_password=dict(type="str", required=False, no_log=True),
			enable_search_indexing=dict(type="bool", required=False),
			enable_password_reset=dict(type="bool", required=False),
			require_two_factor_authentication=dict(type="bool", required=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		params = dict(module.params)
		del params["api_token"]
		req = ModifyUserRequest(**params)

		if not req.has_changes():
			result: dict[str, Any] = {"changed": False}
			if module._diff:
				result["diff"] = {"before": {}, "after": {}}
			module.exit_json(**result)

		current = client.get_user(GetUserRequest(req.userName))

		changes: dict[str, tuple[Any, Any]] = {}
		if req.newUserName is not None and req.newUserName != req.userName:
			changes["userName"] = (req.userName, req.newUserName)
		if req.enableSearchIndexing is not None and req.enableSearchIndexing != current.enableSearchIndexing:
			changes["enableSearchIndexing"] = (current.enableSearchIndexing, req.enableSearchIndexing)
		if req.enablePasswordReset is not None and req.enablePasswordReset != current.recoveryEnabled:
			changes["enablePasswordReset"] = (current.recoveryEnabled, req.enablePasswordReset)
		if req.requireTwoFactorAuthentication is not None and req.requireTwoFactorAuthentication != current.requireTwoFactorAuthentication:
			changes["requireTwoFactorAuthentication"] = (current.requireTwoFactorAuthentication, req.requireTwoFactorAuthentication)
		# password change cannot be detected; force changed if present
		password_change = req.newPassword is not None

		changed = bool(changes) or password_change
		result: dict[str, Any] = {"changed": changed}

		if module._diff:
			before = {k: v[0] for k, v in changes.items()}
			after = {k: v[1] for k, v in changes.items()}
			if password_change:
				before["newPassword"] = "<unknown>"
				after["newPassword"] = "<changed>"
			result["diff"] = {"before": before, "after": after}

		if changed and not module.check_mode:
			_ = client.modify_user(req)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
