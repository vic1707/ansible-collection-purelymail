from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import AddDomainRequest, ListDomainsRequest

DOCUMENTATION = r"""
---
module: add_domain
short_description: Add a domain to your Purelymail account
description:
  - Adds a domain, provided it passes DNS verification checks.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  domain_name:
    description: Name of the domain to add
    required: true
    type: str

notes:
  - The module accepts an internal parameter C(__include_shared) (default: false), this is only used for idempotency and diff generation.

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
- name: Add a new domain
  bofzilla.purelymail.crud.domain.add_domain:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    domain_name: example.com
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			domain_name=dict(type="str", required=True),
			__include_shared=dict(type="bool", required=False, default=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = DomainClient(api)

	try:
		domain_name = module.params["domain_name"]

		existing_domains = client.list_domains(ListDomainsRequest(module.params["__include_shared"]))
		already_exists = any(d.name == domain_name for d in existing_domains.domains)

		result = {"changed": not already_exists}

		if module._diff:
			result["diff"] = {
				"before": existing_domains.as_api_response(),
				"after": existing_domains.concat(
					[ApiDomainInfo.DEFAULT(domain_name)],
				).as_api_response()
				if result["changed"]
				else existing_domains.as_api_response(),
			}

		if result["changed"] and not module.check_mode:
			_ = client.add_domain(AddDomainRequest(domain_name=domain_name))

		module.exit_json(**result)
	except Exception as e:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
