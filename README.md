# vic1707.purelymail

An unofficial Ansible collection for Purelymail's API.

- [Installation and usage](ansible_collections/vic1707/purelymail/README.md)
- [Contributing](CONTRIBUTING.md)

## Publishing

Set `GALAXY_API_KEY` in repository secrets. Update the collection's `galaxy.yml`
version and `CHANGELOG.md`, then tag the commit to publish and push:

```sh
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

CI runs unit tests and lint, builds the collection and publishes it to Galaxy.
No GitHub Release is required. Update module docs alongside code changes.

Prerelease tags such as `v0.1.1-experimental.1` work too; set `galaxy.yml` version
to `0.1.1-experimental.1`. Install explicitly with
`ansible-galaxy collection install vic1707.purelymail:==0.1.1-experimental.1`.

Live API tests are manual: configure secrets `PURELYMAIL_API_TOKEN` and
`PURELYMAIL_USER_PASSWORD`, variable `PURELYMAIL_DOMAIN`, then dispatch **Tests**.
