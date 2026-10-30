# Ansible collection: vic1707.purelymail

An unofficial collection for the [Purelymail API](https://purelymail.com/api).

## Installation

Requires Python 3.12+, ansible-core 2.16+, and a Purelymail API token.
Install Python dependencies in the environment executing the modules:

```sh
python -m pip install 'pydantic>=2,<3' requests
ansible-galaxy collection install vic1707.purelymail
```

## Usage

Use `domains`, `users` and `routing_rules` for desired-state management, or
`crud.*` modules for individual API calls. Read the `canonical` options first:
the defaults can remove resources not included in the desired state.

```sh
ansible-doc --list vic1707.purelymail
ansible-doc vic1707.purelymail.routing_rules
```
