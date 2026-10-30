# Changelog

## [Unreleased]

- Use the `vic1707` collection namespace.
- Isolate mocks and undo patches between unit-test runs so release checks are independent of test order.
- Require ansible-core 2.16+, which supports the Python 3.12 syntax used by this collection.
