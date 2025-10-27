from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import (
	PurelymailAPI,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.routing_client import (
	RoutingClient,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	DeleteRoutingRequest,
)

DOCUMENTATION = r"""
---
module: delete_route
short_description: Delete a Purelymail account's routing rule
description:
  - This module connects to Purelymail API and deletes a specified routing rule.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  routing_rule_id:
    description: Routing rule's id
    required: true
    type: int

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
- name: Get account routing rules
  bofzilla.purelymail.crud.delete_route:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    routing_rule_id: 177013
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			routing_rule_id=dict(type="int", required=True),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = RoutingClient(api)

	try:
		id = module.params["routing_rule_id"]
		existing_routes = client.list_routes()

		result = {"changed": any(r.id == id for r in existing_routes.rules)}

		if module._diff:
			result["diff"] = {
				"before": existing_routes.as_dict(),
				"after": existing_routes.filter(lambda r: r.id != id).as_dict()
				if result["changed"]
				else existing_routes.as_dict(),
			}

		if result["changed"] and not module.check_mode:
			_ = client.delete_route(DeleteRoutingRequest(id))

		module.exit_json(**result)
	except Exception as e:
		import traceback

		module.fail_json(f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
