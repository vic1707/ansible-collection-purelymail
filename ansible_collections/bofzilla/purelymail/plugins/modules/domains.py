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
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

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

EXAMPLES = r"""
# Ensure domain exists without checking the settings
- name: Add example.com with default settings
  bofzilla.purelymail.domains:
    api_token: "{{ purelymail_api_token }}"
    domains:
      - name: example.com

# Ensure domain exists with specified settings
- name: Enable symbolic subaddressing on example.com
  bofzilla.purelymail.domains:
    api_token: "{{ purelymail_api_token }}"
    domains:
      - name: example.com
        symbolic_subaddressing: true

# Canonical mode: remove domains not in the list
- name: Only keep the two listed domains
  bofzilla.purelymail.domains:
    api_token: "{{ purelymail_api_token }}"
    canonical: true
    domains:
      - name: example.com
      - name: example.net

# Trigger DNS recheck
- name: Recheck DNS while keeping other settings unchanged
  bofzilla.purelymail.domains:
    api_token: "{{ purelymail_api_token }}"
    domains:
      - name: example.com
        recheck_dns: true
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

	api = PurelymailAPI(module.params["api_token"])
	client = DomainClient(api)

	try:
		existing_domains = client.list_domains(ListDomainsRequest(False))
		domains = [UpdateDomainSettingsRequest(**d) for d in module.params["domains"]]

		extra_domains = [ed.name for ed in existing_domains.domains if not any(d.name == ed.name for d in domains) and module.params["canonical"]]
		domain_updates = [d for d in domains if any(d.name == ed.name and d.updates(ed) for ed in existing_domains.domains)]
		missing_domains = [d for d in domains if not any(d.name == ed.name for ed in existing_domains.domains)]

		supposed_after = (
			existing_domains.filter(lambda r: r.name not in extra_domains).apply_updates(domain_updates).concat([d.update(ApiDomainInfo.DEFAULT(d.name)) for d in missing_domains])
		)

		result = {
			"changed": bool(extra_domains) or bool(domain_updates) or bool(missing_domains),
			"domains": supposed_after.as_display(),
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
				if domain.updates(ApiDomainInfo.DEFAULT(domain.name), ignore_recheck_dns=True):  # we just created it
					_ = client.update_domain_settings(domain)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
