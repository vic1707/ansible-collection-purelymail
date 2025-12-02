# Contributing

We follow [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our contributions and interactions within this repository.

_If you find inconsistencies or unclear sections, feel free to open an issue or submit a PR._

---

## Development Setup

This repository is fully managed using [mise](https://mise.jdx.dev).

Install all tools and configure the Python `venv`:

```bash
mise install
```

_You can also bring your own `python` & `uv` (check the versions in [.mise.toml](.mise.toml))._

⚠️ Don't forget to create a `.env` file based on [.env.example](.env.example). ⚠️

---

## Syncing the Purelymail API spec

This collection must always match the current Purelymail API version.

Use the provided [script](bin/get_spec) to download/update the API spec:

If the API did not change, `spec.jsonc` will not change either.

Updates on this file are checked upon every PR, you won't be able to merge if the API changed.

If the API did change, a PR should already be opened so changes can be implemented, please rebase on that (or continue it).

---

## Project Structure & Philosophy

This collection aims to be a strict, **1:1** wrapper around the Purelymail API.

### Core principles:

-   **CRUD modules must mirror API endpoints exactly**
    -   same behavior
    -   same fields
    -   same data shapes
-   **No additional abstraction**, except:
    -   private, underscore-prefixed arguments used for idempotency or check-mode internals
-   **Pydantic dataclasses only**
    -   using the shared config in `module_utils/pydantic.py`
-   **Strict fidelity in responses**
    -   returned data must match the API spec exactly
    -   no renaming
    -   no transformations
-   The repo layout is intentionally self-explanatory.
    Follow existing patterns for new modules and clients.

---

## Casing Rules

Ansible parameters are in `snake_case` and returns are in `camelCase` as per API returns.

---

## Testing

### Unit tests

Required for all new modules.

They must cover:

-   API request behavior (call counts)
-   idempotency logic
-   check mode behavior
-   diff mode behavior

Use the existing [examples](ansible_collections/bofzilla/purelymail/tests/unit) as reference.

Run unit tests with
```sh
mise unit-tests
```

### Integration tests

At least one per main module, and one calling all CRUD modules related to the same object.

_Integration tests require a valid `.env` file._

Use the existing [examples](ansible_collections/bofzilla/purelymail/tests/integration) as reference.

Run integration tests:

```bash
mise integration-tests
```

---

## Changelog

Please add a `CHANGELOG.md` entry for any user-visible change.

---

## Repository Layout (short overview)

```
plugins/
  module_utils/
    clients/			# API clients & types
    pydantic.py			# global pydantic config
  modules/
    crud/*				# 1:1 API endpoint wrappers
    *.py				# Ansible-friendly wrappers
tests/
  unit/               # behavior tests
  integration/        # real API tests & workflows
bin/
  get_spec            # updates Purelymail API spec
```
