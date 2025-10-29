from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.billing_client import BillingClient

DOCUMENTATION = r"""
---
module: check_credit_info
short_description: Retrieve Purelymail account credit
description:
  - This module connects to Purelymail API and returns current account credit.
options:
  api_token:
    description: Purelymail API token
    required: true
    type: str

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
- name: Get account credit
  bofzilla.purelymail.crud.billing.check_credit_info:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
credit:
  description: The current credit of the account
  type: float
  returned: always
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(api_token=dict(type="str", required=True, no_log=True)),
	)

	api = PurelymailAPI(module, module.params["api_token"])
	client = BillingClient(api)

	try:
		data = client.check_account_credit()

		res = {"changed": False}

		if module._diff:
			res["diff"] = {
				"before": {"credit": data.credit},
				"after": {"credit": data.credit},
			}

		if not module.check_mode:
			res["credit"] = data.credit

		module.exit_json(**res)
	except Exception as e:
		import traceback

		module.fail_json(f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
