from ansible_collections.bofzilla.purelymail.plugins.modules.routing_rules import RuleSpec


def test_into_create_routing_request_any_address():
	spec = RuleSpec(
		domain_name="example.com",
		target_addresses=[],
		preset="any_address",
		## Gets changed
		match_user="toto",
		prefix=False,
		catchall=True,
	)

	req = spec.into_create_routing_request()
	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	# Changed by `preset="any_address"`
	assert req.matchUser == ""
	assert req.prefix is True
	assert req.catchall is False


def test_into_create_routing_request_catchall_except_valid():
	spec = RuleSpec(
		domain_name="example.com",
		target_addresses=[],
		preset="catchall_except_valid",
		## Gets changed
		match_user="toto",
		prefix=False,
		catchall=False,
	)

	req = spec.into_create_routing_request()
	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	# Changed by `preset="catchall_except_valid"`
	assert req.matchUser == ""
	assert req.prefix is True
	assert req.catchall is True


def test_into_create_routing_request_prefix_match():
	spec = RuleSpec(
		domain_name="example.com",
		target_addresses=[],
		preset="prefix_match",
		match_user="user",
		## Gets changed
		prefix=False,
		catchall=True,
	)

	req = spec.into_create_routing_request()
	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	assert req.matchUser == "user"
	# Changed by `preset="prefix_match"`
	assert req.prefix is True
	assert req.catchall is False


def test_into_create_routing_request_exact_match():
	spec = RuleSpec(
		domain_name="example.com",
		target_addresses=[],
		preset="exact_match",
		match_user="user",
		## Gets changed
		prefix=True,
		catchall=True,
	)

	req = spec.into_create_routing_request()
	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	assert req.matchUser == "user"
	# Changed by `preset="exact_match"`
	assert req.prefix is False
	assert req.catchall is False


def test_into_create_routing_request_manual_values():
	spec = RuleSpec(
		domain_name="example.com",
		target_addresses=[],
		match_user="john",
		prefix=True,
		catchall=True,
	)

	req = spec.into_create_routing_request()
	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	assert req.matchUser == "john"
	assert req.prefix is True
	assert req.catchall is True
