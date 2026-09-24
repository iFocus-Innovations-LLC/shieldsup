# Security policy

`shieldsup` is a **public** Apache-2.0 repository. Treat every file and issue as world-readable.

## Reporting a vulnerability

Do not open a public GitHub issue for a security report.

Use a private [GitHub Security Advisory](https://github.com/iFocus-Innovations-LLC/shieldsup/security/advisories/new) on this repository. Include steps to reproduce, impact, and whether Community (`GRCToolKit`) is affected. If you cannot use advisories, contact the maintainer through the iFocus Innovations LLC GitHub organization.

## Secrets

- No API keys, token-pool credentials, customer data, or `.env` files in git.
- Local secrets stay in an untracked `.env` (see `.env.example`).
- Hosted secrets belong in a secret manager (GCP Secret Manager on the Enterprise path). The Sprint 1 overlay does not read a live secret manager.
- `POOL_REMAINING` is a fake integer for the metering stub. It is not a credential and not a balance of record.

## HITL

The overlay records approve/deny decisions in an append-only AU-2 style log. It does not execute remediation. Do not add a path that applies changes because an event was stored.

## Community pin

OSCAL catalogs and Ansible playbooks are consumed from the `community` submodule. Do not copy them into this repo. A CI check fails the build if `oscal/` or `ansible/playbooks` appear outside that submodule.
