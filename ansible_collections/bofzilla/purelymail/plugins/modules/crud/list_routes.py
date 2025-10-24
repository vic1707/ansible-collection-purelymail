from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import (
	PurelymailAPI,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import (
	RoutingClient,
)

DOCUMENTATION = r"""
---
module: list_routes
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
    support: none
  diff_mode:
    support: none
  idempotent:
    support: none

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Get account routing rules
  bofzilla.purelymail.crud.list_routes:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
routes:
  description: List of routing rules
  type: list
  elements: dict
  contains:
    id:
      description: ID of the routing rule
      type: int
    domain_name:
      description: Domain the rule applies to
      type: str
    match_user:
      description: Local part of the user address
      type: str
    target_addresses:
      description: List of target email addresses
      type: list
      elements: str
    prefix:
      description: Whether match_user is treated as a prefix
      type: bool
    catchall:
      description: Whether this is a catchall rule
      type: bool
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(api_token=dict(type="str", required=True, no_log=True)),
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = RoutingClient(api)

	try:
		data = client.list_routes()
		module.exit_json(
			changed=False,
			routes=[r.__dict__ for r in data.rules],
		)
	except Exception as e:
		module.fail_json(msg=str(e))


if __name__ == "__main__":
	main()
