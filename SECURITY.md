# Security

## Reporting a vulnerability

Use a private [GitHub security advisory](https://github.com/iFocus-Innovations-LLC/shieldsup/security/advisories/new) on this repository. Do not open a public issue for a suspected vulnerability.

## How code reaches main

1. Create a `feature/<topic>` branch. Do not commit or push to `main`.
2. Run `scripts/security-scan.sh` before opening a pull request.
3. Open a pull request. GitHub Actions runs the same script (`test`) and CodeQL.
4. Merge only when those checks are green.

Secret scanning push protection blocks known secrets at push time, before a pull request exists.

## What the scan covers

- Unit tests
- Bandit on `api/app`
- `pip-audit` on `api/requirements.txt`
- Gitleaks on git history
- Trivy on the API image and the rendered Helm chart (critical and high; unfixed issues do not fail the scan)
- `helm lint`

After this pipeline is on `main`, the `main` ruleset should require a pull request, the `test` status check, and CodeQL.
