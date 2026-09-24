"""Enterprise overlay API. Records HITL decisions. Does not remediate."""

from __future__ import annotations

from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app import audit
from app.config import ConfigError, pool_remaining, token_mode

app = FastAPI(
    title="GRCToolKit Enterprise overlay",
    version="0.1.0",
    description=(
        "Public Apache-2.0 overlay. HITL events are append-only. "
        "This service never executes remediation."
    ),
)


class HitlEventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = Field(min_length=1, max_length=256)
    action: str = Field(min_length=1, max_length=512)
    model_id: str = Field(min_length=1, max_length=128)
    approx_tokens: int = Field(ge=0, le=10_000_000)
    decision: Literal["approve", "deny"]


class HitlEventOut(BaseModel):
    id: int
    tenant_id: str
    actor: str
    action: str
    timestamp: str
    model_id: str
    approx_tokens: int
    decision: Literal["approve", "deny"]
    token_mode: Literal["byok", "pool"]
    remediation_executed: Literal[False]


class MeteringOut(BaseModel):
    tenant_id: str
    token_mode: Literal["byok", "pool"]
    pool_remaining: int | None


class TenantOut(BaseModel):
    tenant_id: str
    isolated: Literal[False]


def current_tenant(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    if x_tenant_id is None or not x_tenant_id.strip():
        return "local"
    return x_tenant_id.strip()[:128]


def _mode() -> str:
    try:
        return token_mode()
    except ConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/tenant", response_model=TenantOut)
def tenant(tenant_id: str = Depends(current_tenant)) -> TenantOut:
    return TenantOut(tenant_id=tenant_id, isolated=False)


@app.get("/v1/metering", response_model=MeteringOut)
def metering(tenant_id: str = Depends(current_tenant)) -> MeteringOut:
    mode = _mode()
    if mode == "byok":
        return MeteringOut(tenant_id=tenant_id, token_mode="byok", pool_remaining=None)
    try:
        remaining = pool_remaining()
    except ConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return MeteringOut(tenant_id=tenant_id, token_mode="pool", pool_remaining=remaining)


@app.post("/v1/hitl/events", response_model=HitlEventOut, status_code=201)
def create_event(
    body: HitlEventIn,
    tenant_id: str = Depends(current_tenant),
) -> HitlEventOut:
    recorded = audit.insert_event(
        tenant_id=tenant_id,
        actor=body.actor,
        action=body.action,
        model_id=body.model_id,
        approx_tokens=body.approx_tokens,
        decision=body.decision,
        token_mode=_mode(),
    )
    return HitlEventOut.model_validate(recorded)


@app.get("/v1/hitl/events", response_model=list[HitlEventOut])
def list_events(
    tenant_id: str = Depends(current_tenant),
    limit: int = Query(default=50, ge=1, le=200),
    all_tenants: bool = Query(default=False),
) -> list[HitlEventOut]:
    rows = audit.list_events(
        tenant_id=None if all_tenants else tenant_id,
        limit=limit,
    )
    return [HitlEventOut.model_validate(row) for row in rows]
