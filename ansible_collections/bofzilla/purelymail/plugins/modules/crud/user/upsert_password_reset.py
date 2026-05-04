from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import ListPasswordResetRequest, UpsertPasswordResetRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
---
module: upsert_password_reset
short_description: Create or update a password reset method for a user
description:
  - Creates or updates a password reset method (either phone or email) for a Purelymail user.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  user_name:
    description: Full username, e.g. "user@domain.com"
    required: true
    type: str
  type:
    description: Type of password reset, either "email" or "phone"
    required: true
    type: str
    choices: [email, phone]
  target:
    description: Email address or phone number
    required: true
    type: str
  existing_target:
    description: |
      Target from list operation. If provided, update the existing method matching that target instead of creating a new one.
    required: false
    type: str
  description:
    description: Human-readable description
    required: false
    type: str
    default: ""
  allow_mfa_reset:
    description: Whether this method should allow MFA reset
    required: false
    type: bool
    default: true

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
- name: Create an email password reset method
  bofzilla.purelymail.crud.user.upsert_password_reset:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    user_name: user@example.com
    type: email
    target: backup@example.com
    description: Backup mailbox
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			user_name=dict(type="str", required=True),
			type=dict(type="str", required=True, choices=["email", "phone"]),
			target=dict(type="str", required=True),
			existing_target=dict(type="str", required=False),
			description=dict(type="str", required=False, default=""),
			allow_mfa_reset=dict(type="bool", required=False, default=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	try:
		params = dict(module.params)
		del params["api_token"]
		req = UpsertPasswordResetRequest(**params)

		existing = client.list_password_reset(ListPasswordResetRequest(req.userName))

		lookup_target = req.existingTarget or req.target
		current_match = next((m for m in existing.users if m.target == lookup_target), None)

		changed = (req.existingTarget is not None and req.existingTarget != req.target) or not any(
			m.type == req.type and m.target == req.target and m.description == req.description and m.allowMfaReset == req.allowMfaReset for m in existing.users
		)

		result: dict[str, Any] = {"changed": changed}

		if module._diff:
			before = existing.as_api_response()
			if changed:
				items = existing
				if current_match is not None:
					items = items.filter(lambda m, t=lookup_target: m.target != t)

				after = items.concat([ListPasswordResetResponseItem(req.type, req.target, req.description, req.allowMfaReset)]).as_api_response()
			else:
				after = before
			result["diff"] = {"before": before, "after": after}

		if changed and not module.check_mode:
			_ = client.upsert_password_reset(req)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
