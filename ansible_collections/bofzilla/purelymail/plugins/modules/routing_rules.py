from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import RoutingClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateRoutingRequest, DeleteRoutingRequest

DOCUMENTATION = r"""
module: routing_rules
short_description: Manage the global routing rules for a Purelymail account
description:
  - This module allows you to define the desired state of all routing rules for a Purelymail account.
  - You can specify a list of rules to create or update, optionally pruning any extra rules not listed.
  - Each rule can either fully define the parameters (domain_name, match_user, target_addresses, prefix, catchall) or use one of the WebUI presets to simplify common cases.
  - WebUI match presets:
    - (Any address) → C(match_user="", prefix=True, catchall=False)
    - (Any address except valid user address (catchall)) → C(match_user="", prefix=True, catchall=True)
    - (Any address starting with) → C(match_user="<anything you want>", prefix=True, catchall=False)
    - (The exact address) → C(match_user="<anything you want>", prefix=False, catchall=False)
  - When using presets, you can provide the preset name in the rule instead of manually setting prefix/catchall/match_user.
  - By default, this module is `canonical`, meaning it removes any existing rules that are not explicitly defined

options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  canonical:
    description:
      - Canonical means we remove any existing rules not specified in `rules`
      - Should be a list of domain names to be canonical of
      - Defaults to a set of all domain names referenced in C(rules) and currently present on the API
      - Use V([]) to disable
    type: list
    required: false
    elements: str
    default: list of all referenced domains in C(rules) + already present on API
  inferred_safety:
    description:
      - If true, enables best-effort consistency checks inferred from observed Purelymail API behavior.
      - These safeguards are *not* officially documented by Purelymail and may occasionally reject configurations that the API technically accepts.
      - Current rules:
        - Fails if a rule doesn't match a UI preset
        - You can only have one rule of each preset [any_address,catchall_except_valid]
        - Unknown preset fails (technically the API defaultes them to `any_address`)
    type: bool
    required: false
    default: true

  rules:
    description: List of routing rules to apply
    type: list
    elements: dict
    required: true
    suboptions:
      domain_name:
        description: Domain the rule applies to
        type: str
        required: true
      target_addresses:
        description: List of target email addresses for this rule
        type: list
        elements: str
        required: true

      preset:
        description:
          - WebUI preset to use for this rule.
          - V(any_address) → C(match_user="", prefix=True, catchall=False)
          - V(catchall_except_valid) → C(match_user="", prefix=True, catchall=True)
          - V(prefix_match) → C(prefix=True, catchall=False)
          - V(exact_match) → C(prefix=False, catchall=False)
        type: str
        choices: [any_address, catchall_except_valid, prefix_match, exact_match]
        required: false

      match_user:
        description:
          - Local part of the user address
          - Required if no O(preset)
          - Ignored if C(preset=any_address) or C(preset=catchall_except_valid)
        type: str
        required: false
      prefix:
        description:
          - Whether O(match_user) is treated as a prefix 
          - Required if no O(preset)
          - Ignored if O(preset) is used
        type: bool
        required: false
      catchall:
        description:
          - Whether this is a catchall rule 
          - Required if no O(preset)
          - Ignored if O(preset) is used
        type: bool
        required: false

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  idempotent:
    support: full

author:
  - vic1707
"""

EXAMPLES = r"""
# Example 1: Add a new routing rule (non-canonical)
- name: Add a new routing rule
  bofzilla.purelymail.routing_rules:
    api_token: "{{ purelymail_api_token }}"
    canonical: [] # Disable canonical for every domain
    rules:
      - domain_name: example.com
        match_user: "newuser"
        prefix: false
        catchall: false
        target_addresses:
          - "helpdesk@example.com"
      # You can also use presets like in the WebUI
      - domain_name: example.com
        preset: any_address
        target_addresses: ["admin@example.com"]

# Example 2: Replace all existing rules with a single definition
- name: Replace all routing rules
  bofzilla.purelymail.routing_rules:
    api_token: "{{ purelymail_api_token }}"
    canonical: [example.com] # can also be omitted
    rules:
      - domain_name: example.com
        match_user: "support"
        prefix: false
        catchall: false
        target_addresses:
          - "support@example.com"
"""

RETURN = r"""
rules:
  description:
    - The final list of routing rules after applying changes.
    - IDs are excluded since we can't predict them ahead of time.
  returned: success
  type: list
  elements: dict
  contains:
    domainName:
      description: Domain the rule applies to
      type: str
    matchUser:
      description: Local part of the user address
      type: str
    prefix:
      description: Whether matchUser is treated as a prefix
      type: bool
    catchall:
      description: Whether this is a catchall rule
      type: bool
    targetAddresses:
      description: List of target email addresses
      type: list
      elements: str
    preset:
      description:
        - WebUI preset to use for this rule.
        - V(any_address) → C(match_user="", prefix=True, catchall=False)
        - V(catchall_except_valid) → C(match_user="", prefix=True, catchall=True)
        - V(prefix_match) → C(prefix=True, catchall=False)
        - V(exact_match) → C(prefix=False, catchall=False)
      type: str
      choices: [any_address, catchall_except_valid, prefix_match, exact_match]
"""

module_spec = dict(
	argument_spec=dict(
		api_token=dict(type="str", required=True, no_log=True),
		canonical=dict(type="list", elements="str", required=False),
		inferred_safety=dict(type="bool", required=False, default=True),
		rules=dict(
			type="list",
			required=True,
			elements="dict",
			options=dict(
				domain_name=dict(type="str", required=True),
				target_addresses=dict(type="list", elements="str", required=True),
				preset=dict(
					type="str",
					required=False,
					choices=[
						"any_address",
						"catchall_except_valid",
						"prefix_match",
						"exact_match",
					],
				),
				match_user=dict(type="str", required=False),
				prefix=dict(type="bool", required=False),
				catchall=dict(type="bool", required=False),
			),
			required_if=[
				# Waiting for <https://github.com/ansible/ansible/pull/86074>
				# ("preset", None, ["match_user", "prefix", "catchall"], True),
				("preset", "prefix_match", ["match_user"], True),
				("preset", "exact_match", ["match_user"], True),
			],
		),
	),
)


def main():
	module = AnsibleModule(**module_spec, supports_check_mode=True)

	# Waiting for <https://github.com/ansible/ansible/pull/86074> to remove
	for idx, rule in enumerate(module.params["rules"]):
		if rule.get("preset", None) is None and rule.get("match_user", None) is None and rule.get("prefix", None) is None and rule.get("catchall", None) is None:
			module.fail_json(msg=f"rule[{idx}]: preset is None but any of the following are missing: match_user, prefix, catchall found in rules")

	api = PurelymailAPI(module, module.params["api_token"])
	client = RoutingClient(api)

	try:
		existing_rules = client.list_routing_rules()
		rules = [CreateRoutingRequest(**r) for r in module.params["rules"]]

		canonical_domains: None | list[str] = module.params.get("canonical")
		if canonical_domains is None:
			canonical_domains = list[str]({r.domainName for r in rules + existing_rules.rules})

		if module.params["inferred_safety"]:
			for idx, rule in enumerate(rules):
				# Rule 1: must match a known UI preset
				if rule.preset is None:
					module.fail_json(msg=f"Rule nº{idx} doesn't match any existing preset.")

				# Rule 2: certain presets must be unique (even between each others)
				if rule.preset in ("any_address", "catchall_except_valid"):
					conflict_in_rules = any(i != idx and r.preset in ("any_address", "catchall_except_valid") and r.domainName == rule.domainName for i, r in enumerate(rules))
					conflict_in_existing = rule.domainName in module.params["canonical"] and any(
						er.preset in ("any_address", "catchall_except_valid") and er.domainName == rule.domainName for er in existing_rules.rules
					)

					if conflict_in_rules or conflict_in_existing:
						module.fail_json(msg=f"Rule #{idx}: only one `any_address` or `catchall_except_valid` rule is allowed per domain ({rule.domainName}).")

				# Rule 3: C(match_user="", prefix=False, catchall=False) fails as it is a "The exact address" preset but empty `match_user` isn't valid.
				if rule.preset == "exact_match" and rule.matchUser == "":
					module.fail_json(msg=f"Rule nº{idx} technically matches `exact_match` preset but empty 'match_user' isn't allowed.")

		extra_rules = [er.id for er in existing_rules.rules if not any(r.eq(er) for r in rules) and er.domainName in canonical_domains]
		missing_rules = [r for r in rules if not any(r.eq(er) for er in existing_rules.rules)]

		supposed_after = existing_rules.concat(missing_rules).filter(lambda r: r.id not in extra_rules)

		result = {
			"changed": bool(extra_rules) or bool(missing_rules),
			"rules": supposed_after.as_display(),
		}

		if module._diff:
			result["diff"] = {
				"before": existing_rules.as_display(),
				"after": supposed_after.as_display(),
			}

		if not module.check_mode:
			for id in extra_rules:
				client.delete_routing_rule(DeleteRoutingRequest(id))

			for rule in missing_rules:
				client.create_routing_rule(rule)

		module.exit_json(**result)
	except Exception as e:
		import traceback

		module.fail_json(msg=f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
