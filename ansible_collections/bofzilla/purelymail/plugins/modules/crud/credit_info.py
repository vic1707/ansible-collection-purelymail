from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import (
	PurelymailAPI,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.billing_client import (
	BillingClient,
)

DOCUMENTATION = r"""
---
module: credit_info
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
    support: none
  diff_mode:
    support: none
  idempotent:
    support: none

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Get account credit
  bofzilla.purelymail.crud.credit_info:
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
		data = client.account_credit()
		credit_f = float(data.credit)
		module.exit_json(
			changed=False,
			credit=credit_f,
			msg=f"Current credit is {data.credit}",
		)
	except Exception as e:
		import traceback

		module.fail_json(f"{type(e).__name__}: {e}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
