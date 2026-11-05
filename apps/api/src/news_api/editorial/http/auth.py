from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field

from news_api.dependencies import admin_auth, admin_mutation, client_ip
from news_api.editorial.application.auth import deny_token
from news_api.platform.cache import rate_limit
from news_api.platform.errors import (
    DependencyUnavailable,
    RateLimited,
    Unauthorized,
)
from news_api.platform.metrics import ADMIN_AUTH
from news_api.platform.security import (
    admin_auth_configured,
    create_admin_token,
    new_csrf_token,
    verify_admin_password,
)
from news_api.platform.settings import get_settings

router = APIRouter(prefix="/v1/admin/auth", tags=["admin"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response) -> Any:
    settings = get_settings()
    if not admin_auth_configured():
        raise DependencyUnavailable("Admin authentication is not configured.")
    allowed, _, reset = await rate_limit(
        f"login:{client_ip(request)}", settings.login_rate_limit_per_min, 60
    )
    if not allowed:
        raise RateLimited(
            "Too many login attempts. Try again later.",
            headers={"Retry-After": str(max(1, reset - int(time.time())))},
        )
    if payload.email.lower() != settings.admin_email.lower() or not verify_admin_password(
        payload.password
    ):
        ADMIN_AUTH.labels(result="failure").inc()
        raise Unauthorized("Invalid email or password.")
    token, jti = create_admin_token("operator", settings.admin_email)
    csrf = new_csrf_token()
    max_age = settings.admin_session_minutes * 60
    response.set_cookie(
        "sn_admin",
        token,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        "sn_csrf",
        csrf,
        max_age=max_age,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )
    ADMIN_AUTH.labels(result="success").inc()
    return {
        "operator": {"email": settings.admin_email},
        "csrf_token": csrf,
        "expires_in": max_age,
    }


@router.post("/logout")
async def logout(
    request: Request, response: Response, operator: dict[str, Any] = Depends(admin_mutation)
) -> Any:
    await deny_token(operator["jti"], operator["exp"])
    response.delete_cookie("sn_admin", path="/")
    response.delete_cookie("sn_csrf", path="/")
    ADMIN_AUTH.labels(result="logout").inc()
    return {"status": "ok"}


@router.get("/me")
async def me(operator: dict[str, Any] = Depends(admin_auth)) -> Any:
    settings = get_settings()
    return {"operator": {"email": settings.admin_email, "id": operator["id"]}}
