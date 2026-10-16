from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from sentinel_uas.config import Settings
from sentinel_uas.models import Role

api_key_header = APIKeyHeader(name="X-Lab-Token", auto_error=False)


@dataclass(frozen=True)
class Principal:
    role: Role


def _matches(candidate: str, expected: str) -> bool:
    return secrets.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))


async def get_principal(
    request: Request,
    token: str | None = Security(api_key_header),
) -> Principal:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Lab-Token",
        )

    settings: Settings = request.app.state.settings
    token_roles = (
        (settings.observer_token, Role.OBSERVER),
        (settings.operator_token, Role.OPERATOR),
        (settings.auditor_token, Role.AUDITOR),
        (settings.maintainer_token, Role.MAINTAINER),
    )
    for expected, role in token_roles:
        if _matches(token, expected):
            return Principal(role=role)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid X-Lab-Token",
    )


def require_roles(*roles: Role) -> Callable[..., Awaitable[Principal]]:
    async def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{principal.role.value}' is not allowed for this operation",
            )
        return principal

    return dependency
