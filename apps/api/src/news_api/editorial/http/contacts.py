from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure import ops_repo
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import NotFound

router = APIRouter(prefix="/v1/admin", tags=["admin"])

ContactStatus = Literal["new", "read", "closed"]


class ContactStatusUpdate(BaseModel):
    status: ContactStatus


def contact_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "industry": row.get("industry_slug"),
        "name": row["name"],
        "email": row["email"],
        "phone": row.get("phone"),
        "message": row["message"],
        "locale": row["locale"],
        "status": row["status"],
        "source_page": row.get("source_page"),
        "utm": row.get("utm") or {},
        "country": row.get("country"),
        "session_hash": row.get("session_hash"),
        "created_at": row["created_at"],
    }


@router.get("/contacts", dependencies=[Depends(admin_auth)])
async def list_contacts(
    industry: str | None = None, status: str | None = None, limit: int = 100
) -> Any:
    industry_id = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise NotFound(f"No industry with slug '{industry}'.")
        industry_id = channel.id
    rows = await ops_repo.list_contacts(industry_id=industry_id, status=status, limit=limit)
    return {"data": [contact_dto(row) for row in rows]}


@router.patch("/contacts/{contact_id}", dependencies=[Depends(admin_mutation)])
async def update_contact(contact_id: str, payload: ContactStatusUpdate, request: Request) -> Any:
    contact = await ops_repo.get_contact(contact_id)
    if not contact:
        raise NotFound("Contact message not found.")
    await ops_repo.update_contact_status(contact_id, payload.status)
    await record_audit(
        actor=request.state.operator["email"],
        action="contact.status",
        entity="contact_message",
        entity_id=contact_id,
        payload={"to": payload.status},
    )
    updated = await ops_repo.get_contact(contact_id)
    return {"data": contact_dto(updated) if updated else None}


@router.delete(
    "/contacts/{contact_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def delete_contact(contact_id: str, request: Request) -> None:
    if not await ops_repo.delete_contact(contact_id):
        raise NotFound("Contact message not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="contact.erase",
        entity="contact_message",
        entity_id=contact_id,
        payload={"reason": "DSAR"},
    )
