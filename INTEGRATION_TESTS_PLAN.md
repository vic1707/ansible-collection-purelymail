# Integration Test Suite — Redesign

Living document; updated as work progresses. Source of truth for the new
integration test design.

## Goals
- Run against a dedicated, blank Purelymail account (no prod data risk).
- Cover what has actual value: high-level modules, canonical mode, recovery
  method reconciliation, the routing-rules preset matrix.
- Begin from a blank slate, build state up, restore blank state on success or
  failure.
- Trigger via a single `mise run integration-tests` task.

## Required environment

Replace `tests/integration/integration_config.yml.tpl`:

```yaml
PURELYMAIL_API_TOKEN: ${PURELYMAIL_API_TOKEN}
PURELYMAIL_TEST_DOMAIN_PRIMARY:   ${PURELYMAIL_TEST_DOMAIN_PRIMARY}
PURELYMAIL_TEST_DOMAIN_SECONDARY: ${PURELYMAIL_TEST_DOMAIN_SECONDARY}
PURELYMAIL_TEST_DOMAIN_TERTIARY:  ${PURELYMAIL_TEST_DOMAIN_TERTIARY}
PURELYMAIL_USER_PASSWORD:         ${PURELYMAIL_USER_PASSWORD}
PURELYMAIL_API_TLS_VERIFY:        ${PURELYMAIL_API_TLS_VERIFY:-true}
```

DNS not required: `recheck_dns` tests only assert `changed=true`, not DNS pass.

## Architecture decision

- **Multiple ansible-test targets** with shared setup/teardown roles, ordered
  via filename prefixes (ansible-test runs targets alphabetically).
- Setup: `setup_purelymail` role declared as a `meta` dependency by tests that
  need an existing domain.
- Teardown: `purelymail_wipe` standalone target — both runs at the end of the
  suite (as `99_teardown_check`) and is independently invocable for manual
  emptying.
- Per-target `block/rescue/always` cleanup keeps a failure from leaking state
  to subsequent targets.

## Layout

```
tests/integration/targets/
├── setup_purelymail/                 # role, meta-dependency only (not runnable on its own)
│   ├── meta/main.yml
│   └── tasks/main.yml                # idempotent: ensures primary + secondary
├── purelymail_wipe/                  # full account wipe — also runnable manually
│   ├── aliases                       # ensures it runs only when explicitly targeted
│   └── tasks/main.yml
├── 00_preflight/                     # asserts blank state, fails fast
├── 10_domains_crud/                  # add / update / delete + recheck_dns
├── 20_domains_high_level/            # canonical, multi-domain
├── 30_users_crud/                    # full CRUD + recovery + app password
├── 40_users_high_level/              # canonical + recovery reconciliation
├── 50_routing_crud/                  # create / list / delete
├── 60_routing_presets/               # 16-preset matrix (existing tests, moved)
├── 70_routing_high_level/            # canonical scoping per-domain
├── 80_billing/                       # check_credit_info
├── 90_lookup/                        # ownership_code module + lookup
└── 99_teardown_check/                # runs purelymail_wipe + asserts blank
```

## Mise tasks

```toml
[integration-tests]
depends = ["clean", "generate-integration-config"]
dir = "ansible_collections/bofzilla/purelymail"
run  = "ansible-test integration --coverage --python-interpreter $(which python)"

["integration-tests:wipe"]
depends = ["generate-integration-config"]
dir = "ansible_collections/bofzilla/purelymail"
run  = "ansible-test integration --python-interpreter $(which python) purelymail_wipe"
```

## Test plan (per target)

### `setup_purelymail` (meta role)
- `add_domain` primary (idempotent).
- `add_domain` secondary (idempotent).
- Tertiary NOT added here; only `20_domains_high_level` adds it.

### `purelymail_wipe`
1. `routing_rules` rules=[] canonical=[primary, secondary, tertiary].
2. `users` users=[] canonical=true.
3. Best-effort `delete_domain` for tertiary, secondary, primary.
4. Assert `list_domains` returns 0 non-shared domains.

### `00_preflight`
- Assert `list_domains` non-shared count == 0.
- Assert `list_routing_rules` count == 0.
- Assert `check_credit_info.credit > 0`.
- On failure: `fail` pointing the user to `mise run integration-tests:wipe`.

### `10_domains_crud`
- depends `setup_purelymail`.
- `add_domain` primary again → idempotent.
- `update_domain_settings allow_account_reset=false` → changed=true; idempotent.
- `update_domain_settings recheck_dns=true` → changed=true (always).
- Mixed (recheck + setting) → changed=true.
- Check-mode test: declare a change, assert changed=true, re-list and confirm
  unchanged on the API.
- Diff-mode test: assert diff.before/after present.
- always: restore primary defaults.

### `20_domains_high_level`
- depends `setup_purelymail`.
- `domains` canonical=false, list=[primary, secondary, tertiary] → tertiary
  added, changed=true.
- Re-run → idempotent.
- `domains` canonical=true, list=[primary, secondary] → tertiary removed.
- Re-run → idempotent.
- Update primary's `allow_account_reset` via high-level → changed=true.
- Check-mode test: declare a settings change, confirm `domains` key in result,
  no real change.
- always: ensure tertiary is deleted.

### `30_users_crud`
- depends `setup_purelymail`.
- create_user → idempotent.
- get_user assertions.
- modify_user (`enable_search_indexing=false`) → idempotent.
- upsert_password_reset (email, then phone) — both with idempotency.
- list_password_resets returns 2.
- delete_password_reset specific target → idempotent.
- **delete_password_reset with no target** → wipes all (regression for fix #4).
- create_app_password → returns password, changed=true.
- delete_app_password → changed=true.
- delete_user → idempotent.
- always: best-effort `delete_user`.

### `40_users_high_level`
- depends `setup_purelymail`.
- 2 users with email recovery via `users`.
- Re-run → idempotent.
- Change user1's recovery email → only user1's reset methods reconciled.
- canonical=true with only user1 → user2 deleted.
- always: `users` users=[] canonical=true.

### `50_routing_crud`
- depends `setup_purelymail`.
- create_routing_rule → idempotent.
- list_routing_rules → captured id.
- delete_routing_rule → idempotent.
- always: `routing_rules` rules=[] canonical=[primary].

### `60_routing_presets`
- depends `setup_purelymail`.
- The existing 16-combo matrix moved verbatim, with a per-combo cleanup
  (`routing_rules` rules=[] canonical=[primary]) before each combo.
- `missing_preset_or_settings` failure-mode test kept.
- always: rules=[] canonical=[primary].

### `70_routing_high_level`
- depends `setup_purelymail`.
- Add a rule directly on secondary via `crud.routing.create_routing_rule`.
- Run `routing_rules` canonical=[primary] → secondary rule untouched.
- Run canonical=[primary, secondary] → secondary rule deleted.
- always: rules=[] canonical=[primary, secondary].

### `80_billing`
- `check_credit_info` → `credit` is a non-negative float.

### `90_lookup`
- `crud.domain.get_ownership_code` module → `code` & `value` present.
- `purelymail_ownership_code` lookup → same.

### `99_teardown_check`
- Run `purelymail_wipe` tasks.
- Assert blank state at the end.

## Build progress

Legend: ☐ todo · ◐ in-progress · ✓ done

- ✓ Update `integration_config.yml.tpl` & `.env.example`
- ✓ Delete old targets (`crud.*`, `full_*`, `routing_rules`, `purelymail_ownership_code`)
- ✓ Create `setup_purelymail` role
- ✓ Create `purelymail_wipe` target (with `aliases`)
- ✓ Create `00_preflight`
- ✓ Create `10_domains_crud`
- ✓ Create `20_domains_high_level`
- ✓ Create `30_users_crud`
- ✓ Create `40_users_high_level`
- ✓ Create `50_routing_crud`
- ✓ Move/rebuild `60_routing_presets`
- ✓ Create `70_routing_high_level`
- ✓ Create `80_billing`
- ✓ Create `90_lookup`
- ✓ Create `99_teardown_check`
- ✓ Update `.config/tasks.mise.toml` (`integration-tests:wipe`)
- ✓ `mise run lint` passes (0 failures)
- ✓ `mise run unit-tests` passes (199 + 8 + 1)
- ☐ Smoke-run `mise run integration-tests:wipe` once user has new account creds
- ☐ Smoke-run full `mise run integration-tests` once user has new account creds
- ☐ Delete `/tmp/_pm_preset_matrix_backup` after suite verified green
