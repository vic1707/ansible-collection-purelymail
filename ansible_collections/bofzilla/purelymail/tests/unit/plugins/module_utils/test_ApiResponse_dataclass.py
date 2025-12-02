import pydantic
import pytest

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.response_wrapper import ApiError, ApiSuccess, parse_api_response
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import CheckCreditResponse, EmptyResponse, ListRoutingResponse

MOCK_SUCCESSES = [
	(
		{
			"result": {"rules": [{"prefix": True, "catchall": False, "domainName": "example.com", "matchUser": "toto", "targetAddresses": ["admin@example.com"], "id": 1}]},
			"type": "success",
		},
		ListRoutingResponse,
	),
	({"result": {"credit": "19.1607994830137318004587841289974404320987654320987654320987654320987598"}, "type": "success"}, CheckCreditResponse),
	({"result": {}, "type": "success"}, EmptyResponse),
]
MOCK_ERRORS = [
	{"code": "invalidToken", "message": "Token not valid.", "type": "error"},
]
MOCK_BAD_RESPONSES = [
	({"result": {"something": 12}, "type": "success"}, EmptyResponse),
	({"result": {"credit": "not-a-number"}, "type": "success"}, CheckCreditResponse),
	({"result": {"rules": [{"id": "invalid"}]}, "type": "success"}, ListRoutingResponse),
]


def test_api_success():
	for success, response_type in MOCK_SUCCESSES:
		res = parse_api_response(success, response_type)
		assert isinstance(res, ApiSuccess)
		assert isinstance(res.result, response_type)


def test_api_failures():
	for success in MOCK_ERRORS:
		res = parse_api_response(success, EmptyResponse)
		assert isinstance(res, ApiError)


def test_bad_api_responses():
	for success, response_type in MOCK_BAD_RESPONSES:
		with pytest.raises(pydantic.ValidationError):
			parse_api_response(success, response_type)
