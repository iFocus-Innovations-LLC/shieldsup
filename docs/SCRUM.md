# Scrum — GRCToolKit Enterprise overlay

Sprint length: **2 weeks**. Capacity assumption: 1–2 engineers plus a product owner, about 20–25 points.

## Cadence

| Ceremony | When | Outcome |
|----------|------|---------|
| Planning | First day | Sprint goal, stories pulled into the Sprint column, owners |
| Daily | 15 minutes | What moved, what is blocked, what is next |
| Review | Last day | Demo the local stack: Community pin, one HITL event, BYOK vs pool stub |
| Retro | After review | One process change written into this doc or the next sprint goal |

## Board

Milestone **Sprint 1** holds S1-0 through S1-8 (filed as issues #1–#9). Labels: `type:story|spike|bug`, `area:auth|audit|metering|platform|docs`, `priority:p0|p1`.

GitHub Project columns (create once with org `project` scope):

1. **Backlog**
2. **Sprint**
3. **In Progress**
4. **Review**
5. **Done**

```bash
gh auth refresh -s project,read:project
gh project create --owner iFocus-Innovations-LLC --title "GRCToolKit Enterprise"
```

Sprint 1 issues are closed on the milestone. The Project board is optional tracking; the milestone is the source of truth until the org token includes `project` scope.

## Definition of done

A story is Done only when all of these are true:

- Pull request into `dev` (docs-only fixes may target `main` during a freeze), with CODEOWNERS review
- CI green: lint, unit tests, open-core copy check, Trivy filesystem scan
- No secrets, customer data, or real token-pool credentials in the diff
- HITL changes stay append-only and never auto-remediate
- Community MIT notice stays on the submodule; this repo stays Apache-2.0
- README still describes the Community pin and the Enterprise boundary

## Sprint 1 goal

A developer can clone this public repo, pin Community, run a local stack, record a HITL approve/deny event, and see a BYOK vs pooled-token stub — without copying OSCAL catalogs or Ansible playbooks into this repo.

## Non-goals

Robotics probe catalogs, hosted ADK schedulers, real token billing, multi-tenant SaaS, FedRAMP claims, and a proprietary EULA.
