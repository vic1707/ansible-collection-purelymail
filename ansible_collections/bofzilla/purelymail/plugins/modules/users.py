from typing import Any

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ListPasswordResetResponseItem
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	CreateUserRequest,
	DeletePasswordResetRequest,
	DeleteUserRequest,
	GetUserRequest,
	ListPasswordResetRequest,
	ModifyUserRequest,
	UpsertPasswordResetRequest,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError
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
  elements: str
"""

def _split_email(name: str) -> tuple[str, str]:
	if "@" not in name:
		raise ValueError(f"User name must be a full email address, got {name!r}")
	user, domain = name.rsplit("@", 1)
	return user, domain


def _desired_methods(entry: dict[str, Any]) -> list[dict[str, Any]]:
	"""The reset methods inferred from `recovery_email` / `recovery_phone` fields."""
	out: list[dict[str, Any]] = []
	if entry.get("recovery_email"):
		out.append(
			{
				"type": "email",
				"target": entry["recovery_email"],
				"description": entry.get("recovery_email_description") or "",
				"allowMfaReset": entry["recovery_email_allow_mfa_reset"],
			}
		)
	if entry.get("recovery_phone"):
		out.append(
			{
				"type": "phone",
				"target": entry["recovery_phone"],
				"description": entry.get("recovery_phone_description") or "",
				"allowMfaReset": entry["recovery_phone_allow_mfa_reset"],
			}
		)
	return out


def _method_matches(item: ListPasswordResetResponseItem, desired: dict[str, Any]) -> bool:
	return item.type == desired["type"] and item.target == desired["target"] and item.description == desired["description"] and item.allowMfaReset == desired["allowMfaReset"]


def _build_create_request(entry: dict[str, Any]) -> CreateUserRequest:
	user, domain = _split_email(entry["name"])
	return CreateUserRequest(
		user_name=user,
		domain_name=domain,
		password=entry["password"],
		enable_password_reset=entry.get("enable_password_reset", True),
		recovery_email=entry.get("recovery_email") or "",
		recovery_email_description=entry.get("recovery_email_description") or "",
		recovery_phone=entry.get("recovery_phone") or "",
		recovery_phone_description=entry.get("recovery_phone_description") or "",
		enable_search_indexing=entry.get("enable_search_indexing", True),
		send_welcome_email=entry.get("send_welcome_email") or False,
	)


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
	desired: list[dict[str, Any]] = module.params["users"]

	# --- name validation + duplicate check ---
	seen: set[str] = set()
	for idx, entry in enumerate(desired):
		try:
			_split_email(entry["name"])
		except ValueError as err:
			module.fail_json(msg=f"users[{idx}]: {err}")
		if entry["name"] in seen:
			module.fail_json(msg=f"users[{idx}]: duplicate name {entry['name']!r}")
		seen.add(entry["name"])

	try:
		existing = client.list_users()
		existing_set = set(existing.users)

		desired_names = [e["name"] for e in desired]
		extra_users = [u for u in existing.users if canonical and u not in desired_names]

		# Pre-create plan for users that don't exist yet
		creates: list[CreateUserRequest] = []
		for entry in desired:
			if entry["name"] in existing_set:
				continue
			if not entry.get("password"):
				module.fail_json(msg=f"users: {entry['name']!r} does not exist yet, `password` is required to create it")
			creates.append(_build_create_request(entry))

		# Per-user planning for already-existing users
		existing_user_plans: list[dict[str, Any]] = []
		for entry in desired:
			if entry["name"] not in existing_set:
				continue

			current = client.get_user(GetUserRequest(entry["name"]))

			# settings deltas
			modify_kwargs: dict[str, Any] = {"user_name": entry["name"]}
			settings_changed = False

			if entry["enable_search_indexing"] != current.enableSearchIndexing:
				modify_kwargs["enable_search_indexing"] = entry["enable_search_indexing"]
				settings_changed = True
			if entry["enable_password_reset"] != current.recoveryEnabled:
				modify_kwargs["enable_password_reset"] = entry["enable_password_reset"]
				settings_changed = True
			if entry["require_two_factor_authentication"] != current.requireTwoFactorAuthentication:
				modify_kwargs["require_two_factor_authentication"] = entry["require_two_factor_authentication"]
				settings_changed = True

			# password handling
			pw_mode = entry.get("password_mode") or default_password_mode
			password_will_change = False
			if entry.get("password") and pw_mode == "update-if-provided":
				modify_kwargs["new_password"] = entry["password"]
				password_will_change = True

			modify_req = ModifyUserRequest(**modify_kwargs) if (settings_changed or password_will_change) else None

			# recovery methods reconciliation: always canonical for declared kinds
			declared_methods = _desired_methods(entry)

			listed = client.list_password_reset(ListPasswordResetRequest(entry["name"]))
			current_methods = list(listed.users)

			# Methods to remove:
			#   - existing methods of a kind we declare but with mismatched fields
			#   - existing methods of a kind explicitly emptied (handled the same way:
			#     declared_methods doesn't include that kind, but we still want to delete it).
			# We want full canonical for both email and phone (they are always declared,
			# even if as ""). So remove every existing method that doesn't match a declared one.
			methods_to_remove: list[ListPasswordResetResponseItem] = [m for m in current_methods if not any(_method_matches(m, d) for d in declared_methods)]
			methods_to_add: list[dict[str, Any]] = [d for d in declared_methods if not any(_method_matches(m, d) for m in current_methods)]

			existing_user_plans.append(
				{
					"entry": entry,
					"modify_req": modify_req,
					"settings_changed": settings_changed,
					"password_will_change": password_will_change,
					"methods_to_add": methods_to_add,
					"methods_to_remove": methods_to_remove,
					"current_methods": current_methods,
					"declared_methods": declared_methods,
				}
			)

		# --- compute changed ---
		changed = bool(extra_users) or bool(creates) or any(p["modify_req"] is not None or p["methods_to_add"] or p["methods_to_remove"] for p in existing_user_plans)

		# --- diff ---
		def _user_after(entry: dict[str, Any], plan: dict[str, Any] | None) -> dict[str, Any]:
			view: dict[str, Any] = {"name": entry["name"]}
			if plan is None:
				# new user
				view["enableSearchIndexing"] = entry["enable_search_indexing"]
				view["recoveryEnabled"] = entry["enable_password_reset"]
				view["requireTwoFactorAuthentication"] = entry["require_two_factor_authentication"]
				view["resetMethods"] = _desired_methods(entry)
				if entry.get("password"):
					view["password"] = "<set>"
				return view

			req: ModifyUserRequest | None = plan["modify_req"]
			if req is not None:
				if req.enableSearchIndexing is not None:
					view["enableSearchIndexing"] = req.enableSearchIndexing
				if req.enablePasswordReset is not None:
					view["recoveryEnabled"] = req.enablePasswordReset
				if req.requireTwoFactorAuthentication is not None:
					view["requireTwoFactorAuthentication"] = req.requireTwoFactorAuthentication
				if req.newPassword is not None:
					view["password"] = "<changed>"

			view["resetMethods"] = plan["declared_methods"]
			return view

		result: dict[str, Any] = {
			"changed": changed,
			"users": sorted([n for n in existing.users if n not in extra_users] + [c.email for c in creates]),
		}

		if module._diff:
			before_users = sorted(existing.users)
			after_names = sorted([n for n in existing.users if n not in extra_users] + [c.email for c in creates])

			before_detailed: list[dict[str, Any]] = []
			after_detailed: list[dict[str, Any]] = []

			for u in extra_users:
				before_detailed.append({"name": u, "_state": "deleted"})

			for plan in existing_user_plans:
				if plan["modify_req"] is None and not plan["methods_to_add"] and not plan["methods_to_remove"]:
					continue
				entry = plan["entry"]
				before_detailed.append(
					{
						"name": entry["name"],
						"resetMethods": [m.as_api_response() for m in plan["current_methods"]],
					}
				)
				after_detailed.append(_user_after(entry, plan))

			for c in creates:
				entry = next(e for e in desired if e["name"] == c.email)
				after_detailed.append(_user_after(entry, None))

			result["diff"] = {
				"before": {"users": before_users, "details": before_detailed},
				"after": {"users": after_names, "details": after_detailed},
			}

		if not module.check_mode:
			# 1) deletes
			for name in extra_users:
				_ = client.delete_user(DeleteUserRequest(name))

			# 2) creates
			for create_req in creates:
				_ = client.create_user(create_req)

			# 3) modifications + recovery methods reconciliation
			for plan in existing_user_plans:
				entry = plan["entry"]
				if plan["modify_req"] is not None:
					_ = client.modify_user(plan["modify_req"])
				for to_remove in plan["methods_to_remove"]:
					_ = client.delete_password_reset(DeletePasswordResetRequest(entry["name"], to_remove.target))
				for to_add in plan["methods_to_add"]:
					_ = client.upsert_password_reset(
						UpsertPasswordResetRequest(
							user_name=entry["name"],
							type=to_add["type"],
							target=to_add["target"],
							description=to_add["description"],
							allow_mfa_reset=to_add["allowMfaReset"],
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
