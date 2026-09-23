# Open-core contract

**Product:** GRCToolKit Enterprise  
**Overlay repo:** [shieldsup](https://github.com/iFocus-Innovations-LLC/shieldsup) (Apache-2.0, public)  
**Community repo:** [GRCToolKit](https://github.com/iFocus-Innovations-LLC/GRCToolKit) (MIT)

Enterprise value is hosted runtime, token pools, SLAs, and training. It is not a closed fork of compliance logic.

## Consume Community by pin

The overlay vendors Community as a **git submodule** at `community/`, pinned to the freeze tag **`v2.1.0-qa-demo`**. That tag is an immutable QA/demo pin. Do not move it forward from this repo to track `main`.

```bash
git submodule update --init
git -C community describe --tags --exact-match
```

`docker compose` builds the Community UI from `community/Dockerfile`. `make community-up` does the same. Neither path copies catalogs or playbooks into the overlay tree.

## Allowed in this repo

- FastAPI overlay (health, tenant stub, HITL audit log, metering stub)
- Compose and Make wrappers that build Community from the submodule
- Docs, Scrum templates, and CI that lint and test the overlay
- References and links to Community paths

## Forbidden in this repo

- A copy of `oscal/` anywhere except inside `community/`
- A copy of `ansible/playbooks` anywhere except inside `community/`
- A fork or rewrite of `ai-agent/grc-compliance-engine.js`
- Secrets, customer data, or real token-pool credentials
- Relicensing this overlay away from Apache-2.0, or treating Community as proprietary

`scripts/check-open-core.sh` fails CI when a forbidden copy is present. The `community/` submodule is excluded from that search.

## What stays in Community

- OSCAL catalogs and compliance documents
- Ansible playbooks, including Shields Up / OWASP LLM probes
- Browser AI engine and BYOK one-shot analysis
- Robotics probe implementation (still gated on the Community production tag)

## What the overlay adds in Sprint 1

- `X-Tenant-Id` stub (default `local`; not tenant isolation)
- Append-only HITL audit events (no remediation execution)
- `TOKEN_MODE=byok|pool` with a fake pool balance
