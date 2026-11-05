from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure import ops_repo
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import Conflict, NotFound, ValidationProblem

router = APIRouter(prefix="/v1/admin", tags=["admin"])

LeadStatus = Literal["new", "routed", "contacted", "qualified", "closed", "spam"]
PartnerStatus = Literal["active", "disabled"]


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    note: str | None = Field(default=None, max_length=500)


class LeadAssign(BaseModel):
    partner_id: str | None = None


class PartnerCreate(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    contact_email: EmailStr
    regions: list[str] = Field(default_factory=list)


class PartnerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    contact_email: EmailStr | None = None
    status: PartnerStatus | None = None
    weight: float | None = Field(default=None, gt=0, le=10)
    regions: list[str] | None = None


def lead_dto(row: dict[str, Any], *, include_pii: bool = True) -> dict[str, Any]:
    payload = {
        "id": str(row["id"]),
        "industry": row.get("industry_slug"),
        "partner_id": row.get("partner_id"),
        "partner_name": row.get("partner_name"),
        "kind": row["kind"],
        "locale": row["locale"],
        "status": row["status"],
        "consent_version": row["consent_version"],
        "consent_at": row["consent_at"],
        "source_page": row.get("source_page"),
        "article_id": row.get("article_id"),
        "utm": row.get("utm"),
        "created_at": row["created_at"],
        "updated_at": row.get("updated_at"),
    }
    if include_pii:
        payload.update(
            {
                "name": row["name"],
                "email": row["email"],
                "phone": row.get("phone"),
                "company": row.get("company"),
                "message": row.get("message"),
            }
        )
    return payload


def partner_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "industry": row.get("industry_slug"),
        "name": row["name"],
        "contact_email": row["contact_email"],
        "status": row["status"],
        "weight": float(row["weight"]),
        "regions": row.get("regions") or [],
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


@router.get("/leads", dependencies=[Depends(admin_auth)])
async def list_leads(industry: str | None = None, status: str | None = None) -> Any:
    industry_id = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise NotFound(f"No industry with slug '{industry}'.")
        industry_id = channel.id
    rows = await ops_repo.list_leads(industry_id=industry_id, status=status)
    return {"data": [lead_dto(row) for row in rows]}


@router.patch("/leads/{lead_id}", dependencies=[Depends(admin_mutation)])
async def update_lead(lead_id: str, payload: LeadStatusUpdate, request: Request) -> Any:
    lead = await ops_repo.get_lead(lead_id)
    if not lead:
        raise NotFound("Lead not found.")
    await ops_repo.update_lead_status(lead_id, payload.status)
    await ops_repo.add_lead_event(
        lead_id,
        actor=request.state.operator["email"],
        action="status",
        payload={"from": lead["status"], "to": payload.status, "note": payload.note},
    )
    await record_audit(
        actor=request.state.operator["email"],
        action="lead.status",
        entity="lead",
        entity_id=lead_id,
        payload={"to": payload.status},
    )
    updated = await ops_repo.get_lead(lead_id)
    return {"data": lead_dto(updated) if updated else None}


@router.post("/leads/{lead_id}/assign", dependencies=[Depends(admin_mutation)])
async def assign_lead(lead_id: str, payload: LeadAssign, request: Request) -> Any:
    lead = await ops_repo.get_lead(lead_id)
    if not lead:
        raise NotFound("Lead not found.")
    if payload.partner_id:
        partner_rows = await ops_repo.list_partners(lead["industry_slug"])
        if not any(str(item["id"]) == payload.partner_id for item in partner_rows):
            raise ValidationProblem("Partner does not belong to this lead's channel.")
    await ops_repo.assign_lead(lead_id, payload.partner_id)
    await ops_repo.add_lead_event(
        lead_id,
        actor=request.state.operator["email"],
        action="reassigned" if lead.get("partner_id") else "routed",
        payload={"partner_id": payload.partner_id},
    )
    await record_audit(
        actor=request.state.operator["email"],
        action="lead.assign",
        entity="lead",
        entity_id=lead_id,
        payload={"partner_id": payload.partner_id},
    )
    updated = await ops_repo.get_lead(lead_id)
    return {"data": lead_dto(updated) if updated else None}


@router.get("/leads/{lead_id}/export", dependencies=[Depends(admin_auth)])
async def export_lead(lead_id: str, request: Request) -> Any:
    lead = await ops_repo.get_lead(lead_id)
    if not lead:
        raise NotFound("Lead not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="lead.export",
        entity="lead",
        entity_id=lead_id,
    )
    return {"data": lead_dto(lead)}


@router.delete(
    "/leads/{lead_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def delete_lead(lead_id: str, request: Request) -> None:
    if not await ops_repo.delete_lead(lead_id):
        raise NotFound("Lead not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="lead.erase",
        entity="lead",
        entity_id=lead_id,
        payload={"reason": "DSAR"},
    )


@router.get("/partners", dependencies=[Depends(admin_auth)])
async def list_partners(industry: str | None = None) -> Any:
    industry_id = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise NotFound(f"No industry with slug '{industry}'.")
        industry_id = channel.id
    rows = await ops_repo.list_partners(industry_id)
    return {"data": [partner_dto(row) for row in rows]}


@router.post("/partners", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_partner(payload: PartnerCreate, request: Request) -> Any:
    channel = await channels_repo.get_channel(payload.industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{payload.industry}'.")
    row = await ops_repo.create_partner(
        industry_id=channel.id,
        name=payload.name,
        contact_email=str(payload.contact_email),
        regions=payload.regions,
    )
    if not row:
        raise Conflict("That channel already has a partner.")
    await record_audit(
        actor=request.state.operator["email"],
        action="partner.create",
        entity="partner",
        entity_id=str(row["id"]),
        payload={"industry": channel.slug},
    )
    return {"data": partner_dto({**row, "industry_slug": channel.slug})}


@router.patch("/partners/{partner_id}", dependencies=[Depends(admin_mutation)])
async def update_partner(partner_id: str, payload: PartnerUpdate, request: Request) -> Any:
    fields = payload.model_dump(exclude_unset=True)
    if "contact_email" in fields and fields["contact_email"] is not None:
        fields["contact_email"] = str(fields["contact_email"])
    row = await ops_repo.update_partner(partner_id, fields)
    if not row:
        raise NotFound("Partner not found or no changes supplied.")
    await record_audit(
        actor=request.state.operator["email"],
        action="partner.update",
        entity="partner",
        entity_id=partner_id,
        payload={"fields": sorted(fields.keys())},
    )
    return {"data": partner_dto(row)}


@router.delete(
    "/partners/{partner_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def disable_partner(partner_id: str, request: Request) -> None:
    row = await ops_repo.update_partner(partner_id, {"status": "disabled"})
    if not row:
        raise NotFound("Partner not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="partner.disable",
        entity="partner",
        entity_id=partner_id,
    )
