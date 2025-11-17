from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	AddDomainRequest,
	DeleteDomainRequest,
	ListDomainsRequest,
	UpdateDomainSettingsRequest,
)

DOCUMENTATION = r"""
module: domains
short_description: Manage domains for a Purelymail account
description:
  - This module allows you to define the desired state of all domains for a Purelymail account.
  - By default, this module is `canonical`, meaning it removes any domains that are not explicitly defined

options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

  canonical:
    description: Canonical means we remove any domain not specified in `domains`
    type: boolean
    required: false
    default: true

  domains:
    description: List of domains to apply
    type: list
    elements: dict
    required: true
    suboptions:
      name:
        description: Domain name
        type: str
        required: true
      allow_account_reset:
        description: Whether account reset is allowed for this domain
        required: false
        type: bool
      symbolic_subaddressing:
        description: Enable or disable symbolic subaddressing
        required: false
        type: bool
      recheck_dns:
        description: Trigger recheck of domain DNS configuration
        required: false
        type: bool
        default: false

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
    details:
      - Future state is idealised and based on previous Purelymail's defaults, it assumes DNS check passes, please report incorrect defaults.
  idempotent:
    support: full

author:
  - vic1707
"""

EXAMPLES = r""""""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			canonical=dict(type="bool", required=False, default=True),
			domains=dict(
				type="list",
				required=True,
				elements="dict",
				options=dict(
					name=dict(type="str", required=True),
					allow_account_reset=dict(type="bool", required=False),
					symbolic_subaddressing=dict(type="bool", required=False),
					recheck_dns=dict(type="bool", required=False, default=False),
				),
			),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = DomainClient(api)

	try:
		existing_domains = client.list_domains(ListDomainsRequest(False))
		domains = [UpdateDomainSettingsRequest(**d) for d in module.params["domains"]]

		extra_domains = [ed.name for ed in existing_domains.domains if not any(d.name == ed.name for d in domains) and module.params["canonical"]]
		domain_updates = [d for d in domains if any(d.updates(ed) and d.name == ed.name for ed in existing_domains.domains)]
		missing_domains = [d for d in domains if not any(d.name == ed.name for ed in existing_domains.domains)]

		supposed_after = (
			existing_domains.filter(lambda r: r.name not in extra_domains).apply_updates(domain_updates).concat([d.update(ApiDomainInfo.DEFAULT(d.name)) for d in missing_domains])
		)

		result = {
			"changed": bool(extra_domains) or bool(domain_updates) or bool(missing_domains),
			"rules": supposed_after.as_display(),
		}

		if module._diff:
			result["diff"] = {
				"before": existing_domains.as_display(),
				"after": supposed_after.as_display(),
			}

		if not module.check_mode:
			for name in extra_domains:
				_ = client.delete_domain(DeleteDomainRequest(name))

			for domain in domain_updates:
				_ = client.update_domain_settings(domain)

			for domain in missing_domains:
				_ = client.add_domain(AddDomainRequest(domain.name))
				if domain.updates(ApiDomainInfo.DEFAULT(domain.name)):
					_ = client.update_domain_settings(domain)

		module.exit_json(**result)
	except Exception as e:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
