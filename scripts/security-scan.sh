#!/usr/bin/env bash
# Run this before opening a pull request. CI runs the same script.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TOOL_DIR="${ROOT}/.tools"
mkdir -p "$TOOL_DIR"

GITLEAKS_VERSION="8.30.1"
TRIVY_VERSION="0.74.0"

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

download_verified() {
  local url="$1"
  local checksum="$2"
  local dest="$3"
  local tmp
  tmp="$(mktemp)"
  curl -fsSL "$url" -o "$tmp"
  local got
  got="$(sha256_file "$tmp")"
  if [[ "$got" != "$checksum" ]]; then
    echo "Checksum mismatch for ${url}" >&2
    echo "expected ${checksum}" >&2
    echo "got      ${got}" >&2
    rm -f "$tmp"
    exit 1
  fi
  mkdir -p "$dest"
  tar -xzf "$tmp" -C "$dest"
  rm -f "$tmp"
}

gitleaks_asset() {
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) echo "gitleaks_${GITLEAKS_VERSION}_darwin_arm64.tar.gz b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5" ;;
    Darwin-x86_64) echo "gitleaks_${GITLEAKS_VERSION}_darwin_x64.tar.gz dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709" ;;
    Linux-x86_64) echo "gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb" ;;
    Linux-aarch64) echo "gitleaks_${GITLEAKS_VERSION}_linux_arm64.tar.gz e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080" ;;
    *)
      echo "No gitleaks binary for $(uname -s)-$(uname -m)" >&2
      exit 1
      ;;
  esac
}

trivy_asset() {
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) echo "trivy_${TRIVY_VERSION}_macOS-ARM64.tar.gz 1caada5e0e2091909357c7525d3aa76f4b660b13821bc143b190c7483e31cc11" ;;
    Darwin-x86_64) echo "trivy_${TRIVY_VERSION}_macOS-64bit.tar.gz 472816f6888dda689d075c30254d4210b4d1035acf365aa72332f584c2f60485" ;;
    Linux-x86_64) echo "trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz 2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a" ;;
    Linux-aarch64) echo "trivy_${TRIVY_VERSION}_Linux-ARM64.tar.gz b94ce1976bbf3c15b514b605ee88be7c6d94a29be2302847ff01cb794d47aad5" ;;
    *)
      echo "No Trivy binary for $(uname -s)-$(uname -m)" >&2
      exit 1
      ;;
  esac
}

install_tool() {
  local name="$1"
  local version="$2"
  local repo="$3"
  local asset checksum dest
  read -r asset checksum <<<"$4"
  dest="${TOOL_DIR}/${name}-${version}"
  if [[ ! -x "${dest}/${name}" ]]; then
    download_verified \
      "https://github.com/${repo}/releases/download/v${version}/${asset}" \
      "$checksum" \
      "$dest"
  fi
  echo "${dest}/${name}"
}

echo "==> Python tests, Bandit, and dependency audit"
if [[ ! -x "${ROOT}/.venv/bin/python" ]]; then
  python3 -m venv "${ROOT}/.venv"
fi
PY="${ROOT}/.venv/bin/python"
"$PY" -m pip install --disable-pip-version-check -q \
  -r api/requirements.txt \
  -r api/requirements-dev.txt \
  pip-audit \
  bandit
"$PY" -m pytest
"$PY" -m bandit -r api/app -ll
"$PY" -m pip_audit -r api/requirements.txt

echo "==> Secret scan"
GITLEAKS="$(install_tool gitleaks "$GITLEAKS_VERSION" gitleaks/gitleaks "$(gitleaks_asset)")"
"$GITLEAKS" detect --source "$ROOT" --redact --no-banner --exit-code 1

echo "==> Image scan"
require_cmd docker
docker build -t shieldsup-api:security-scan "${ROOT}/api"
TRIVY="$(install_tool trivy "$TRIVY_VERSION" aquasecurity/trivy "$(trivy_asset)")"
"$TRIVY" image \
  --severity CRITICAL,HIGH \
  --ignore-unfixed \
  --exit-code 1 \
  shieldsup-api:security-scan

echo "==> Helm chart"
require_cmd helm
helm lint charts/shieldsup
rendered="$(mktemp "${TMPDIR:-/tmp}/shieldsup-rendered.XXXXXX")"
mv "$rendered" "${rendered}.yaml"
rendered="${rendered}.yaml"
helm template shieldsup charts/shieldsup --namespace shieldsup >"$rendered"
"$TRIVY" config \
  --severity CRITICAL,HIGH \
  --exit-code 1 \
  "$rendered"
rm -f "$rendered"

echo "Security scan passed."
