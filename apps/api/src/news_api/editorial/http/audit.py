from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from news_api.dependencies import admin_auth
from news_api.editorial.infrastructure.repo import list_audit

router = APIRouter(prefix="/v1/admin/audit", tags=["admin"])


@router.get("", dependencies=[Depends(admin_auth)])
async def audit_log(action: str | None = None, limit: int = 200) -> Any:
    rows = await list_audit(action=action, limit=limit)
    return {"data": rows}
