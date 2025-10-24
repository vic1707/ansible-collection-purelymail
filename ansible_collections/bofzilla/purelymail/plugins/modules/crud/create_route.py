from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import (
	PurelymailAPI,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import (
	RoutingClient,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	CreateRoutingRequest,
)

DOCUMENTATION = r"""
---
module: create_route
short_description: Create a new routing rule
description:
  - This module connects to Purelymail API and creates a new routing rule
  - This module is idempotent and supports check mode.
  - WebUI match cases:
    - (Any address) → C(match_user="", prefix=True, catchall=False)
    - (Any address except valid user address (catchall)) → C(match_user="", prefix=True, catchall=True)
    - (Any address starting with) → C(match_user="<anything you want>", prefix=True, catchall=False)
    - (The exact address) → C(match_user="<anything you want>", prefix=False, catchall=False)
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  domain_name:
    description: Domain the rule applies to
    type: str
    required: true
  match_user:
    description: Local part of the user address
    type: str
    required: true
  target_addresses:
    description: List of target email addresses
    type: list
    elements: str
    required: true
  prefix:
    description: Whether match_user is treated as a prefix
    type: bool
    required: true
  catchall:
    description: Whether this is a catchall rule
    type: bool
    default: false
    required: false

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Create routing rule
  bofzilla.purelymail.crud.create_route:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"

    domain_name: example.com
    match_user: admin
    target_addresses: ["example@example.com"]
    prefix: false
    catchall: false
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			domain_name=dict(type="str", required=True),
			match_user=dict(type="str", required=True),
			target_addresses=dict(type="list", elements="str", required=True),
			prefix=dict(type="bool", required=True),
			catchall=dict(type="bool", required=False, default=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = RoutingClient(api)

	try:
		route_spec = module.params
		del route_spec["api_token"]
		route = CreateRoutingRequest(**route_spec)

		existing_routes = client.list_routes()

		if any(route.matches(r) for r in existing_routes.rules):
			module.exit_json(changed=False)

		if module.check_mode:
			module.exit_json(changed=True)

		_ = client.create_route(route)
		module.exit_json(changed=True)
	except Exception as e:
		module.fail_json(msg=str(e))


if __name__ == "__main__":
	main()
