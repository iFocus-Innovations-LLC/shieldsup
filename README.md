# GRCToolKit Enterprise (Shields Up)

Private enterprise control plane. Not open source.

This repository is the **GRCToolKit Enterprise** product. The product name stays GRCToolKit Enterprise. The repo name is `shieldsup`. Local work lives in `~/dev/shieldup`.

Community Edition remains the separate public MIT product at [GRCToolKit](https://github.com/iFocus-Innovations-LLC/GRCToolKit). This codebase does not pin, submodule, or ship Community.

## What this MVP includes

- A lightweight HTTP API with `GET /healthz`
- A Helm chart that installs that API on any conformant Kubernetes
- A local **kind** test path on this machine

It does not include PostgreSQL, OIDC, HITL audit, Hugging Face model pull, or a mobile client yet. Those follow after this health slice.

## License

Proprietary. All rights reserved by iFocus Innovations LLC. The Apache-2.0 `LICENSE` file on `main` is a leftover from the public stub and is not the license for new enterprise code in this branch.

## Test the MVP (kind)

Do not install this chart into the Community GKE cluster. Use a local kind cluster.

```bash
# Install tools once (Homebrew)
brew install kind helm kubectl

# Create a local cluster
kind create cluster --name shieldsup

# Build and load the image
docker build -t shieldsup-api:mvp ./api
kind load docker-image shieldsup-api:mvp --name shieldsup

# Install
kubectl create namespace shieldsup
helm upgrade --install shieldsup ./charts/shieldsup \
  --namespace shieldsup \
  --set image.repository=shieldsup-api \
  --set image.tag=mvp \
  --set image.pullPolicy=Never

# Prove health
kubectl -n shieldsup rollout status deploy/shieldsup-api
kubectl -n shieldsup port-forward svc/shieldsup-api 8080:80
# in another shell:
curl -sS http://127.0.0.1:8080/healthz
```

Expect `{"status":"ok"}`.

## Run the API without Kubernetes

```bash
python3 -m venv .venv
.venv/bin/pip install -r api/requirements.txt
.venv/bin/uvicorn app.main:app --app-dir api --port 8080
curl -sS http://127.0.0.1:8080/healthz
```

## Architecture notes

- Helm is the supported install path for any cloud Kubernetes (EKS, AKS, GKE, kind, k3s).
- The same lightweight API is the contract for a later mobile client and a private Hugging Face model pin.
- HITL decisions, when added, are append-only and never execute remediation.
