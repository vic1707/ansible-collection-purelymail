from ansible.module_utils.basic import AnsibleModule

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

DOCUMENTATION = r"""
---
module: get_ownership_code
short_description: Retrieve the Purelymail ownership DNS record value
description:
  - Gets the DNS record value used to verify domain ownership with Purelymail.
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
- name: Retrieve ownership verification code
  bofzilla.purelymail.crud.domain.get_ownership_code:
    api_token: "{{ lookup('env','PURELYMAIL_API_TOKEN') }}"
"""

RETURN = r"""
code:
  description:
    - The full DNS TXT record value required for domain verification.
    - "*SENSITIVE*: This value should be treated as secret."
  type: str
  returned: success
  sample:
    - purelymail_ownership_proof=dQw4w9WgXcQ

value:
  description:
    - The extracted verification code, without the "purelymail_ownership_proof=" prefix.
    - "*WARNING*: This is a non-standard custom field added for convenience. It is not part of the Purelymail API response."
    - "*SENSITIVE*: This value should be treated as secret."
  type: str
  returned: success
  sample:
    - dQw4w9WgXcQ
"""


def main():
	module = AnsibleModule(
		argument_spec=dict(api_token=dict(type="str", required=True, no_log=True)),
		supports_check_mode=True,
	)

	api = PurelymailAPI(module.params["api_token"])
	client = DomainClient(api)

	try:
		data = client.get_ownership_code()
		data = {"code": data.code, "value": data.value}
		res = {"changed": False}

		if module._diff:
			res["diff"] = {"before": data, "after": data}

		if not module.check_mode:
			res.update(data)

		module.no_log_values = {data["code"], data["value"]}
		module.exit_json(**res)
	except ApiError as err:  # pragma: no cover
		module.fail_json(msg=f"Purelymail API error: {err}", exception=err)
	except Exception as err:  # pragma: no cover
		import traceback

		module.fail_json(msg=f"{type(err).__name__}: {err}", exception=traceback.format_exc())


if __name__ == "__main__":
	main()
