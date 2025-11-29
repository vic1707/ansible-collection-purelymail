from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.billing_client import BillingClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

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
- name: Get account credit
  bofzilla.purelymail.crud.billing.check_credit_info:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
credit:
  description: The current credit of the account
  type: float
  returned: success
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(api_token=dict(type="str", required=True, no_log=True)),
	)

	api = PurelymailAPI(module.params["api_token"])
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
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
