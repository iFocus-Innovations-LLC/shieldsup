# S1-6 — Identity path spike

**Question:** For Sprint 2, should the overlay authenticate with GCP Identity-Aware Proxy (IAP), Identity Platform, or Firebase Authentication?

**Recommendation:** **GCP Identity-Aware Proxy** in front of the hosted overlay (Cloud Run or GKE).

## Why IAP

The Enterprise hosted runtime is already planned on GCP (Cloud Run / GKE, Secret Manager, later ADK). IAP puts a Google-authenticated identity on the request before the app sees it. Sprint 2 can map that identity into the audit `actor` field and drop the `X-Tenant-Id: local` default for deployed environments.

IAP does not require a second user store, and it matches a private or organization-gated demo. The Sprint 1 API stays a stub: no production IdP is wired in this sprint.

## Why not the others yet

| Option | Fit | Defer because |
|--------|-----|----------------|
| **Identity Platform** | Customer users, SAML, multi-tenant SaaS | Multi-tenant SaaS is out of scope. Revisit when a customer must sign in with their own IdP. |
| **Firebase Authentication** | Mobile and consumer login | No mobile client in this overlay. Community mobile work stays in the Community roadmap. |

## Sprint 2 exit

- Hosted overlay reachable only through IAP
- Audit `actor` taken from the IAP identity, not a client-supplied header
- Local `docker compose` still defaults to tenant `local` with no IdP
- Still no remediation execution
