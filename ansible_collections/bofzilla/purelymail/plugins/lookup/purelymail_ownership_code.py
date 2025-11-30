from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.domain_client import DomainClient
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError

DOCUMENTATION = r"""
---
lookup: purelymail_ownership_code
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
- name: Get just the TXT record
  ansible.builtin.debug:
    msg: >-
      {{ lookup("bofzilla.purelymail.purelymail_ownership_code", api_token=lookup('env','PURELYMAIL_API_TOKEN').code }}

- name: Get just the verification code
  ansible.builtin.debug:
    msg: >-
      {{ lookup("bofzilla.purelymail.purelymail_ownership_code", api_token=lookup('env','PURELYMAIL_API_TOKEN').value }}
"""

RETURN = r"""
_raw:
  description:
    - The object provides two useful attributes:
        - C(code): The full DNS TXT value (e.g. C(purelymail_ownership_proof=dQw4w9WgXcQ))
        - C(value): The extracted verification code without the prefix (e.g. C(dQw4w9WgXcQ))
    - Both values are sensitive and should be treated as secrets.
  type: list
  returned: always
  sample:
    - code: purelymail_ownership_proof=dQw4w9WgXcQ
      value: dQw4w9WgXcQ
"""


class LookupModule(LookupBase):
	def run(self, terms, variables=None, **kwargs):
		assert len(terms) == 0
		self.set_options(var_options=variables, direct=kwargs)
		api_token = self.get_option("api_token")

		api = PurelymailAPI(api_token)
		client = DomainClient(api)

		try:
			return [client.get_ownership_code()]
		except ApiError as err:  # pragma: no cover
			AnsibleError(f"Purelymail API error: {err}")
		except Exception as err:  # pragma: no cover
			AnsibleError(f"{type(err).__name__}: {err}")
