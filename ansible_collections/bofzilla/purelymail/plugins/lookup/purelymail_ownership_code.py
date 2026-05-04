from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

DOCUMENTATION = r"""
---
name: purelymail_ownership_code
short_description: Retrieve the Purelymail ownership DNS record value
description:
  - This lookup retrieves the DNS TXT record value used to verify domain ownership
    with Purelymail.
options:
  api_token:
    description: Purelymail API token.
    required: true
    type: str

author:
  - vic1707
"""

EXAMPLES = r"""
- name: Get the full TXT record value
  ansible.builtin.debug:
    msg: >-
      {{ lookup('bofzilla.purelymail.purelymail_ownership_code', api_token=lookup('env', 'PURELYMAIL_API_TOKEN')).code }}

- name: Get just the verification code (without prefix)
  ansible.builtin.debug:
    msg: >-
      {{ lookup('bofzilla.purelymail.purelymail_ownership_code', api_token=lookup('env', 'PURELYMAIL_API_TOKEN')).value }}
"""

RETURN = r"""
_raw:
  description:
    - A list with a single dict containing two keys:
        - C(code): The full DNS TXT value (e.g. C(purelymail_ownership_proof=dQw4w9WgXcQ))
        - C(value): The extracted verification code without the prefix (e.g. C(dQw4w9WgXcQ))
    - Both values are sensitive and should be treated as secrets.
  type: list
  elements: dict
  returned: always
  sample:
    - code: purelymail_ownership_proof=dQw4w9WgXcQ
      value: dQw4w9WgXcQ
"""


class LookupModule(LookupBase):
	def run(self, terms, variables=None, **kwargs):
		if terms:
			raise AnsibleError("purelymail_ownership_code lookup does not accept positional terms.")
		self.set_options(var_options=variables, direct=kwargs)
		api_token = self.get_option("api_token")

		api = PurelymailAPI(api_token)
		client = DomainClient(api)

		try:
			resp = client.get_ownership_code()
			return [{"code": resp.code, "value": resp.value}]
		except ApiError as err:  # pragma: no cover
			raise AnsibleError(f"Purelymail API error: {err}") from err
		except Exception as err:  # pragma: no cover
			raise AnsibleError(f"{type(err).__name__}: {err}") from err
