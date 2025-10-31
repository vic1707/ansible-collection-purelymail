from ansible.module_utils.basic import ModuleArgumentSpecValidator
from ansible.module_utils.common.arg_spec import ValidationResult

from ansible_collections.bofzilla.purelymail.plugins.modules.routing_rules import module_spec

VALIDATOR = ModuleArgumentSpecValidator(**module_spec)


def test_any_address_preset():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "any_address",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
				}
			],
		}
	)
	assert len(res.error_messages) == 0
	assert len(res._warnings) == 0


def test_catchall_except_valid_preset():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "catchall_except_valid",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
				}
			],
		}
	)
	assert len(res.error_messages) == 0
	assert len(res._warnings) == 0


def test_prefix_match_preset():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "prefix_match",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
					"match_user": "info",
				}
			],
		}
	)
	assert len(res.error_messages) == 0
	assert len(res._warnings) == 0


def test_prefix_match_preset_requires_match_user():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "prefix_match",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
				}
			],
		}
	)
	assert len(res.error_messages) == 1
	assert res.error_messages[0] == "preset is prefix_match but any of the following are missing: match_user found in rules"
	assert len(res._warnings) == 0


def test_exact_match_preset():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "exact_match",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
					"match_user": "admin",
				}
			],
		}
	)
	assert len(res.error_messages) == 0
	assert len(res._warnings) == 0


def test_exact_match_requires_match_user():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [
				{
					"preset": "exact_match",
					"domain_name": "example.com",
					"target_addresses": ["admin@example.com"],
				}
			],
		}
	)
	assert len(res.error_messages) == 1
	assert res.error_messages[0] == "preset is exact_match but any of the following are missing: match_user found in rules"
	assert len(res._warnings) == 0


# Waiting for <https://github.com/ansible/ansible/pull/86074>
# def test_no_prefix_requires_match_user_and_prefix():
# 	res: ValidationResult = VALIDATOR.validate(
# 		{
# 			"api_token": "dQw4w9WgXcQ",
# 			"rules": [
# 				{
# 					"domain_name": "example.com",
# 					"target_addresses": ["admin@example.com"],
# 				}
# 			],
# 		}
# 	)
# 	assert 1 == len(res.error_messages)
# 	assert "preset is None but any of the following are missing: match_user, prefix, catchall found in rules" == res.error_messages[0]
# 	assert 0 == len(res._warnings)


def test_valid_no_prefix():
	res: ValidationResult = VALIDATOR.validate(
		{
			"api_token": "dQw4w9WgXcQ",
			"rules": [{"domain_name": "example.com", "target_addresses": ["admin@example.com"], "catchall": True, "prefix": True, "match_user": "admin"}],
		}
	)
	assert len(res.error_messages) == 0
	assert len(res._warnings) == 0
