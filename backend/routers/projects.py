"""Project management routes — CRUD for projects and API keys."""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.project import Project, APIKey
from backend.schemas import ProjectCreate, ProjectResponse, APIKeyCreate, APIKeyResponse
from backend.auth import hash_api_key

router = APIRouter(prefix="/v1/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    project = Project(name=data.name, description=data.description)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/api-keys", response_model=APIKeyResponse, status_code=201)
async def create_api_key(
    project_id: UUID,
    data: APIKeyCreate = APIKeyCreate(),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key for a project. The full key is only shown once."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    # Generate key
    raw_key = APIKey.generate_key()
    key_hash = hash_api_key(raw_key)
    key_prefix = raw_key[:12]

    api_key = APIKey(
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=data.name,
        project_id=project_id,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)

    # Return with full key (only time it's visible)
    return APIKeyResponse(
        id=api_key.id,
        key_prefix=api_key.key_prefix,
        name=api_key.name,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        full_key=raw_key,
    )


@router.get("/{project_id}/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """List API keys for a project (prefixes only, not full keys)."""
    result = await db.execute(
        select(APIKey).where(APIKey.project_id == project_id).order_by(APIKey.created_at.desc())
    )
    return result.scalars().all()
