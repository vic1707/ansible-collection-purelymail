from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.module_inputs import UserInput
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	DeletePasswordResetRequest,
	DeleteUserRequest,
	GetUserRequest,
	UpsertPasswordResetRequest,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import GetUserResponse
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.user_client import UserClient

DOCUMENTATION = r"""
module: users
short_description: Manage users for a Purelymail account
description:
  - This module allows you to define the desired state of all users for a Purelymail account.
  - Each user can be created, modified (settings + password), and have its
    password-reset methods (recovery email + phone) reconciled to the declared state.
  - By default, this module is `canonical`, meaning it removes any user not specified in C(users).
  - Recovery methods are derived from O(users[].recovery_email) and O(users[].recovery_phone)
    (with their `_description` and `_allow_mfa_reset` companions). For existing users they
    are reconciled fully; non-empty target ensures the method exists exactly with the declared
    description and MFA flag; empty target deletes any reset method of that kind.

options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  canonical:
    description: Canonical means we remove any user not specified in C(users).
    type: bool
    required: false
    default: true

  password_mode:
    description:
      - Default password handling for all entries in C(users).
      - V(update-if-provided) updates the password whenever O(users[].password) is given (always reports `changed`).
      - V(ignore-if-exists) only sets the password at user creation; for already-existing users the password field is ignored.
      - Each user entry can override this with O(users[].password_mode).
    type: str
    required: false
    default: update-if-provided
    choices: [update-if-provided, ignore-if-exists]

  users:
    description: List of users to apply
    type: list
    elements: dict
    required: true
    suboptions:
      name:
        description: Full username (e.g. C(user@example.com))
        type: str
        required: true
      password:
        description:
          - Password for the user.
          - Required when the user does not yet exist.
          - For existing users, behavior depends on O(users[].password_mode) / O(password_mode).
        type: str
        required: false
      password_mode:
        description: Per-user override of O(password_mode).
        type: str
        required: false
        choices: [update-if-provided, ignore-if-exists]

      enable_search_indexing:
        description: Whether search indexing should be enabled for this user.
        type: bool
        required: false
        default: true
      enable_password_reset:
        description: Whether this user can have their password reset.
        type: bool
        required: false
        default: true
      require_two_factor_authentication:
        description: Whether this user requires 2FA for login.
        type: bool
        required: false
        default: false

      recovery_email:
        description:
          - Recovery email address for the user.
          - Empty string means no email recovery method (existing ones will be removed for this user).
        type: str
        required: false
        default: ""
      recovery_email_description:
        description: Human-readable description for the recovery email method.
        type: str
        required: false
        default: ""
      recovery_email_allow_mfa_reset:
        description: Whether the recovery email is allowed to reset MFA.
        type: bool
        required: false
        default: true

      recovery_phone:
        description:
          - Recovery phone for the user.
          - Empty string means no phone recovery method (existing ones will be removed for this user).
        type: str
        required: false
        default: ""
      recovery_phone_description:
        description: Human-readable description for the recovery phone method.
        type: str
        required: false
        default: ""
      recovery_phone_allow_mfa_reset:
        description: Whether the recovery phone is allowed to reset MFA.
        type: bool
        required: false
        default: true

      send_welcome_email:
        description: Send a welcome email when the user is created. Ignored for existing users.
        type: bool
        required: false
        default: false

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
    details:
      - Password values are never displayed; password updates are reported as C(<changed>).
  idempotent:
    support: partial
    details:
      - When O(password_mode=update-if-provided) and a password is given for an existing user,
        the module always reports a change for that user (the API gives no way to verify the password).

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Ensure two users with desired settings and recovery info
  bofzilla.purelymail.users:
    api_token: "{{ purelymail_api_token }}"
    canonical: false
    users:
      - name: alice@example.com
        password: "{{ alice_password }}"
        password_mode: ignore-if-exists
        require_two_factor_authentication: true
        recovery_email: alice-recovery@example.com
        recovery_email_description: backup
      - name: bob@example.com
        password: "{{ bob_password }}"
        # explicitly no recovery methods
        recovery_email: ""
        recovery_phone: ""

- name: Canonical \u2014 only keep listed users
  bofzilla.purelymail.users:
    api_token: "{{ purelymail_api_token }}"
    users:
      - name: only-one@example.com
        password: "{{ pwd }}"
"""

RETURN = r"""
users:
  description: The final list of users on the account after applying changes.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: Full username.
      type: str
    enableSearchIndexing:
      description: Whether search indexing is enabled for this user.
      type: bool
    recoveryEnabled:
      description: Whether this user can use password recovery.
      type: bool
    requireTwoFactorAuthentication:
      description: Whether this user requires 2FA for login.
      type: bool
    enableSpamFiltering:
      description: Whether spam filtering is enabled for this user.
      type: bool
    resetMethods:
      description: List of password reset methods for this user.
      type: list
      elements: dict
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			canonical=dict(type="bool", required=False, default=True),
			password_mode=dict(
				type="str",
				required=False,
				default="update-if-provided",
				choices=["update-if-provided", "ignore-if-exists"],
			),
			users=dict(
				type="list",
				required=True,
				elements="dict",
				options=dict(
					name=dict(type="str", required=True),
					password=dict(type="str", required=False, no_log=True),
					password_mode=dict(
						type="str",
						required=False,
						choices=["update-if-provided", "ignore-if-exists"],
					),
					enable_search_indexing=dict(type="bool", required=False, default=True),
					enable_password_reset=dict(type="bool", required=False, default=True),
					require_two_factor_authentication=dict(type="bool", required=False, default=False),
					recovery_email=dict(type="str", required=False, default=""),
					recovery_email_description=dict(type="str", required=False, default=""),
					recovery_email_allow_mfa_reset=dict(type="bool", required=False, default=True),
					recovery_phone=dict(type="str", required=False, default=""),
					recovery_phone_description=dict(type="str", required=False, default=""),
					recovery_phone_allow_mfa_reset=dict(type="bool", required=False, default=True),
					send_welcome_email=dict(type="bool", required=False, default=False),
				),
			),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = UserClient(api)

	default_password_mode: str = module.params["password_mode"]
	canonical: bool = module.params["canonical"]

	users: list[UserInput] = []
	for idx, params in enumerate(module.params["users"]):
		email = params["name"]
		if any(u.email == email for u in users):
			module.fail_json(msg=f"users[{idx}]: duplicate name {params['name']!r}")
		if "@" not in email:
			module.fail_json(msg=f"users[{idx}]: User name must be a full email address, got {params['name']!r}")
		users.append(UserInput(**params))

	try:
		existing = client.list_users()
		existing_users = {name: client.get_user(GetUserRequest(name)) for name in existing.users}
		desired_users = {user.email: user for user in users}

		extra_users = [name for name in existing.users if canonical and name not in desired_users]
		missing_users = [u for u in users if u.email not in existing_users]
		for user in missing_users:
			if not user.password:
				module.fail_json(msg=f"users: {user.email!r} does not exist yet, `password` is required to create it")

		updates = []
		method_deletes = []
		method_upserts = []
		supposed_after = {name: user for name, user in existing_users.items() if name not in extra_users}

		for user in users:
			current = existing_users.get(user.email) or GetUserResponse.expectedFromUserInput(user, from_create=True)
			wanted = GetUserResponse.expectedFromUserInput(
				user,
				enableSpamFiltering=current.enableSpamFiltering,
			)
			new_password = user.password if user.email in existing_users and user.password and (user.passwordMode or default_password_mode) == "update-if-provided" else None
			update = current.modify_request(user.email, wanted, new_password=new_password)
			if update.has_changes():
				updates.append(update)
				supposed_after[user.email] = current.update(update, wanted.resetMethods)
			else:
				supposed_after[user.email] = wanted

			method_deletes += [(user.email, m) for m in current.resetMethods if m not in wanted.resetMethods]
			method_upserts += [(user.email, m) for m in wanted.resetMethods if m not in current.resetMethods]

		result: dict[str, Any] = {
			"changed": bool(extra_users or missing_users or updates or method_deletes or method_upserts),
			"users": [supposed_after[name].as_display(name) for name in sorted(supposed_after)],
		}

		if module._diff:
			result["diff"] = {
				"before": [existing_users[name].as_display(name) for name in sorted(existing_users)],
				"after": [supposed_after[name].as_display(name) for name in sorted(supposed_after)],
			}
			for user in result["diff"]["before"]:
				user["password"] = "<unknown>"
			for user in result["diff"]["after"]:
				if any(missing.email == user["name"] for missing in missing_users):
					user["password"] = "<set>"
				if any(update.userName == user["name"] and update.newPassword for update in updates):
					user["password"] = "<changed>"

		if not module.check_mode:
			for name in extra_users:
				_ = client.delete_user(DeleteUserRequest(name))

			for user in missing_users:
				_ = client.create_user(user)

			for update in updates:
				_ = client.modify_user(update)

			for user_name, method in method_deletes:
				_ = client.delete_password_reset(DeletePasswordResetRequest(user_name, method.target))

			for user_name, method in method_upserts:
				_ = client.upsert_password_reset(
					UpsertPasswordResetRequest(
						user_name=user_name,
						type=method.type,
						target=method.target,
						description=method.description,
						allow_mfa_reset=method.allowMfaReset,
					)
				)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
