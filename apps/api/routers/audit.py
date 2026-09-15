"""Immutable Security Audit Logs API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.audit import AuditLog
from schemas.audit import AuditLogOut
from core.security import get_current_user, require_roles, User

router = APIRouter(prefix="/audit", tags=["Audit & Governance"])


@router.get("/logs", response_model=List[AuditLogOut])
async def list_audit_logs(
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "AUDITOR"]))
):
    """Queries tamper-evident security audit logs."""
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    if action:
        query = query.where(AuditLog.action == action.upper())
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    query = query.limit(limit)

    results = await db.execute(query)
    return list(results.scalars().all())
