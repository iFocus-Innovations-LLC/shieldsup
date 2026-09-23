# GRCToolKit Enterprise

Public **Apache-2.0** overlay for [GRCToolKit](https://github.com/iFocus-Innovations-LLC/GRCToolKit) Community Edition (MIT).

The product name is **GRCToolKit Enterprise**. This repository (`shieldsup`) is the overlay home. **Shields Up** stays a module and campaign inside Community, not a separate product. Enterprise adds relationship, SLAs, training, token economics, and a hosted runtime path. It does not paywall OSCAL, Ansible, or the AI engine.

| | Community | This overlay |
|--|-----------|----------------|
| Repo | [GRCToolKit](https://github.com/iFocus-Innovations-LLC/GRCToolKit) | [shieldsup](https://github.com/iFocus-Innovations-LLC/shieldsup) |
| License | MIT | Apache-2.0 |
| Role | OSCAL, Ansible, AI engine, Shields Up probes | Pin Community, HITL AU-2 audit log, BYOK vs pool stub |

Robotics probe implementation stays in Community and is still gated there. Do not copy `oscal/` or `ansible/playbooks` into this repo. See [docs/OPEN-CORE.md](docs/OPEN-CORE.md).

## Five-minute local path

```bash
git clone https://github.com/iFocus-Innovations-LLC/shieldsup.git
cd shieldsup
git submodule update --init
cp .env.example .env
docker compose up --build
```

- Community UI (from the pinned submodule): http://localhost:8080
- Overlay API: http://localhost:8090/healthz
- OpenAPI: http://localhost:8090/docs

Record a HITL decision. The overlay stores the event and does not remediate.

```bash
curl -sS -X POST http://localhost:8090/v1/hitl/events \
  -H 'content-type: application/json' \
  -H 'X-Tenant-Id: local' \
  -d '{"actor":"analyst@example.com","action":"review-control","model_id":"gemini-2.0-flash","approx_tokens":120,"decision":"deny"}'
```

Switch the metering stub without putting a real pool credential in git:

```bash
TOKEN_MODE=pool docker compose up --build overlay
curl -sS http://localhost:8090/v1/metering
```

`TOKEN_MODE=byok` (default) means the customer supplies the key. `TOKEN_MODE=pool` returns `POOL_REMAINING`, a fake integer for local demos.

Without Docker, the API alone:

```bash
python3 -m venv .venv
.venv/bin/pip install -r overlay/requirements.txt
AUDIT_DB_PATH=./data/audit.db TOKEN_MODE=byok \
  .venv/bin/uvicorn app.main:app --app-dir overlay --port 8090
```

Community UI without the overlay image:

```bash
make community-up
```

## Sprint 1 boundary

In this sprint the overlay can:

- pin Community at `v2.1.0-qa-demo`
- serve that UI from the submodule
- accept `X-Tenant-Id` (default `local`)
- append HITL approve/deny events (actor, action, timestamp, model id, approximate tokens, decision, token mode)
- report BYOK vs a fake pool balance

It does not run remediation, bill tokens, host ADK schedulers, or isolate tenants.

Scrum cadence and definition of done: [docs/SCRUM.md](docs/SCRUM.md).

## Branches

`main` is stable. `dev` is integration. Day-to-day work lands on `feature/*` via pull request into `dev`. Same model as Community ([RELEASE-BRANCHING.md](https://github.com/iFocus-Innovations-LLC/GRCToolKit/blob/main/docs/RELEASE-BRANCHING.md)).

## Security

Public repository. No secrets, customer data, or real token-pool credentials. Report vulnerabilities in private GitHub Security Advisories. See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE). The Community submodule remains under its own MIT license.
