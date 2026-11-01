# Changelog

## [Unreleased]

- Publish SemVer tags, including prereleases, to Galaxy after CI.
- Run credentialed live API tests only by explicit workflow dispatch.
- Use the `vic1707` collection namespace.
- Isolate mocks and undo patches between unit-test runs so release checks are independent of test order.
- Require ansible-core 2.16+, which supports the Python 3.12 syntax used by this collection.
