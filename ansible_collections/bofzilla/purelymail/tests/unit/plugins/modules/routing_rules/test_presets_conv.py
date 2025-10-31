from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import CreateRoutingRequest


def test_from_preset_any_address():
	req = CreateRoutingRequest(
		domain_name="example.com",
		target_addresses=[],
		preset="any_address",
		## Gets changed
		match_user="toto",
		prefix=False,
		catchall=True,
	)

	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	# Changed by `preset="any_address"`
	assert req.matchUser == ""
	assert req.prefix is True
	assert req.catchall is False
	assert req.preset == "any_address"


def test_from_preset_catchall_except_valid():
	req = CreateRoutingRequest(
		domain_name="example.com",
		target_addresses=[],
		preset="catchall_except_valid",
		## Gets changed
		match_user="toto",
		prefix=False,
		catchall=False,
	)

	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	# Changed by `preset="catchall_except_valid"`
	assert req.matchUser == ""
	assert req.prefix is True
	assert req.catchall is True
	assert req.preset == "catchall_except_valid"


def test_from_preset_prefix_match():
	req = CreateRoutingRequest(
		domain_name="example.com",
		target_addresses=[],
		preset="prefix_match",
		match_user="user",
		## Gets changed
		prefix=False,
		catchall=True,
	)

	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	assert req.matchUser == "user"
	# Changed by `preset="prefix_match"`
	assert req.prefix is True
	assert req.catchall is False
	assert req.preset == "prefix_match"


def test_from_preset_exact_match():
	req = CreateRoutingRequest(
		domain_name="example.com",
		target_addresses=[],
		preset="exact_match",
		match_user="user",
		## Gets changed
		prefix=True,
		catchall=True,
	)

	assert req.domainName == "example.com"
	assert req.targetAddresses == []
	assert req.matchUser == "user"
	# Changed by `preset="exact_match"`
	assert req.prefix is False
	assert req.catchall is False
	assert req.preset == "exact_match"
