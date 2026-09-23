"""Lightweight GRCToolKit Enterprise API."""

from fastapi import FastAPI

app = FastAPI(
    title="GRCToolKit Enterprise",
    version="0.1.0",
    description="Private Shields Up control plane. Health only in this MVP.",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
