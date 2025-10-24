from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import RoutingClient

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
  - Optionally, `only_specified_rules` can be set to true to remove any rules not explicitly defined in the input list.

options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  only_specified_rules:
    description: If true, remove any existing rules not specified in `rules`
    type: bool
    required: false
    default: false

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
    support: none
  diff_mode:
    support: none
  idempotent:
    support: none

author:
  - vic1707
"""

EXAMPLES = r""""""

RETURN = r""""""

module_spec = dict(
	argument_spec=dict(
		api_token=dict(type="str", required=True, no_log=True),
		only_specified_rules=dict(type="bool", required=False, default=False),
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
	module = AnsibleModule(**module_spec)

	# Waiting for <https://github.com/ansible/ansible/pull/86074> to remove
	for idx, rule in enumerate(module.params["rules"]):
		if rule["preset"] is None and rule["match_user"] is None and rule["prefix"] is None and rule["catchall"] is None:
			module.fail_json(msg=f"rule[{idx}]: preset is None but any of the following are missing: match_user, prefix, catchall found in rules")

	api = PurelymailAPI(module, module.params["api_token"])
	client = RoutingClient(api)

	try:
		# TODO
		module.exit_json(changed=True)
	except Exception as e:
		module.fail_json(msg=str(e))


if __name__ == "__main__":
	main()
