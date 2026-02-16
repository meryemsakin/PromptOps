"""Authentication utilities — API key validation."""

from hashlib import sha256
from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.project import APIKey


def hash_api_key(key: str) -> str:
    """Hash an API key for secure storage."""
    return sha256(key.encode()).hexdigest()


async def get_project_id_from_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """
    Validate API key and return the associated project ID.
    Used as a dependency in protected routes.
    """
    key_hash = hash_api_key(x_api_key)

    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True,
        )
    )
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    return api_key.project_id
