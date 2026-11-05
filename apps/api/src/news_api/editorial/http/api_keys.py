from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import (
    count_active_keys,
    create_api_key,
    list_api_keys,
    record_audit,
    revoke_api_key,
)
from news_api.platform.errors import NotFound
from news_api.platform.metrics import API_KEYS_ACTIVE
from news_api.platform.security import generate_api_key

router = APIRouter(prefix="/v1/admin/api-keys", tags=["admin"])


class ApiKeyCreate(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    rate_limit: int = Field(default=600, ge=1, le=10000)


def key_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "label": row["label"],
        "prefix": row["key_prefix"],
        "scopes": list(row.get("scopes") or []),
        "rate_limit": int(row["rate_limit"]),
        "enabled": bool(row["enabled"]),
        "last_used_at": row.get("last_used_at"),
        "created_at": row.get("created_at"),
    }


@router.get("", dependencies=[Depends(admin_auth)])
async def get_keys() -> Any:
    rows = await list_api_keys()
    API_KEYS_ACTIVE.set(await count_active_keys())
    return {"data": [key_dto(row) for row in rows]}


@router.post("", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_key(payload: ApiKeyCreate, request: Request) -> Any:
    plaintext, key_hash, prefix = generate_api_key()
    row = await create_api_key(
        label=payload.label,
        key_hash=key_hash,
        key_prefix=prefix,
        scopes=["read"],
        rate_limit=payload.rate_limit,
    )
    if not row:
        raise NotFound("Could not create API key.")
    await record_audit(
        actor=request.state.operator["email"],
        action="api_key.create",
        entity="api_key",
        entity_id=str(row["id"]),
        payload={"label": payload.label, "prefix": prefix},
    )
    API_KEYS_ACTIVE.set(await count_active_keys())
    return {"data": {**key_dto(row), "key": plaintext}}


@router.delete(
    "/{key_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def revoke_key(key_id: str, request: Request) -> None:
    if not await revoke_api_key(key_id):
        raise NotFound("API key not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="api_key.revoke",
        entity="api_key",
        entity_id=key_id,
    )
    API_KEYS_ACTIVE.set(await count_active_keys())
