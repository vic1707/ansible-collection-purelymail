from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import RoutingClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

DOCUMENTATION = r"""
---
module: list_routing_rules
short_description: Retrieve Purelymail account's defined routing rules
description:
  - This module connects to Purelymail API and returns current routing rules.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: full
    details:
      - This action does not modify state.
  idempotent:
    support: full
    details:
      - This action does not modify state.

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Get account routing rules
  bofzilla.purelymail.crud.routing.list_routing_rules:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
rules:
  description: List of routing rules
  type: list
  elements: dict
  returned: success
  contains:
    id:
      description: ID of the routing rule
      type: int
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
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(api_token=dict(type="str", required=True, no_log=True)),
	)

	api = PurelymailAPI(module.params["api_token"])
	client = RoutingClient(api)

	try:
		rules = client.list_routing_rules().as_api_response()

		res = {"changed": False}

		if module._diff:
			res["diff"] = {"before": rules, "after": rules}

		if not module.check_mode:
			res["rules"] = rules

		module.exit_json(**res)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
