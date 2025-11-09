from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import ListDomainsRequest

DOCUMENTATION = r"""
---
module: list_domains
short_description: List accessible domains on Purelymail account
description:
  - Connects to the Purelymail API and returns the list of accessible domains.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  include_shared:
    description: Include shared (Purelymail-owned) domains in response
    required: false
    type: bool
    default: false
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
- name: List accessible domains
  bofzilla.purelymail.crud.domain.list_domains:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
domains:
  description: List of domains accessible to the account
  type: list
  elements: dict
  returned: success
  contains:
    name:
      description: The domain name
      type: str
    allowAccountReset:
      description: Whether password resets are allowed for users on this domain
      type: bool
    symbolicSubaddressing:
      description: Whether symbolic (“+tag”) subaddressing is enabled for this domain
      type: bool
    isShared:
      description: Whether this domain is a shared Purelymail domain
      type: bool
    dnsSummary:
      description: Summary of the domain’s DNS status
      type: dict
      contains:
        passesMx:
          description: Whether the MX record check passes
          type: bool
        passesSpf:
          description: Whether the SPF record check passes
          type: bool
        passesDkim:
          description: Whether the DKIM record check passes
          type: bool
        passesDmarc:
          description: Whether the DMARC record check passes
          type: bool
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			include_shared=dict(type="bool", required=False, default=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = DomainClient(api)

	try:
		req = ListDomainsRequest(module.params["include_shared"])
		domains = client.list_domains(req).as_api_response()

		res = {"changed": False}

		if module._diff:
			res["diff"] = {"before": domains, "after": domains}

		if not module.check_mode:
			res["domains"] = domains

		module.exit_json(**res)
	except Exception as e:
		import traceback

		module.fail_json(msg=f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
