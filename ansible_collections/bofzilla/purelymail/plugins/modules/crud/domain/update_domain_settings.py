from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.api_types import ApiDomainInfo
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import ListDomainsRequest, UpdateDomainSettingsRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

DOCUMENTATION = r"""
---
module: update_domain_settings
short_description: Update settings for a domain
description:
  - Updates DNS, reset permissions, or symbolic subaddressing for a Purelymail domain.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str
  name:
    description: Domain name to update
    required: true
    type: str
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

notes:
  - The module accepts an internal parameter C(__include_shared) (default: false), this is only used for idempotency and diff generation.

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
    details:
      - Future state is idealised, `recheck_dns` can fail
  idempotent:
    support: full

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Enable symbolic subaddressing
  bofzilla.purelymail.crud.domain.update_domain_settings:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
    name: example.com
    symbolic_subaddressing: true
"""

RETURN = r""""""


def main():
	module = AnsibleModule(
		argument_spec=dict(
			api_token=dict(type="str", required=True, no_log=True),
			name=dict(type="str", required=True),
			allow_account_reset=dict(type="bool", required=False),
			symbolic_subaddressing=dict(type="bool", required=False),
			recheck_dns=dict(type="bool", required=False, default=False),
			__include_shared=dict(type="bool", required=False, default=False),
		),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = DomainClient(api)

	try:
		existing_domains = client.list_domains(ListDomainsRequest(module.params["__include_shared"]))
		current = next((d for d in existing_domains.domains if d.name == module.params["name"]), None)

		if not current:
			module.fail_json(msg=f"Error: domain '{module.params['name']}' does not exist.")
		assert isinstance(current, ApiDomainInfo)  # TODO: remove when `ty` supports it

		req_params = module.params
		del req_params["api_token"], req_params["__include_shared"]
		req = UpdateDomainSettingsRequest(**req_params)

		result = {"changed": req.updates(current)}

		if module._diff:
			result["diff"] = {"before": current, "after": req.update(current)}

		if result["changed"] and not module.check_mode:
			_ = client.update_domain_settings(req)

		module.exit_json(**result)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
