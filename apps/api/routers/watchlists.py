"""Watchlists and Watchlist Entries API Router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.watchlist import Watchlist, WatchlistEntry
from schemas.watchlist import WatchlistOut, WatchlistCreate, WatchlistEntryOut, WatchlistEntryCreate
from core.security import get_current_user, require_roles, User

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.get("", response_model=List[WatchlistOut])
async def list_watchlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all active operational watchlists (stolen vehicles, wanted persons, priority surveillance)."""
    result = await db.execute(select(Watchlist).order_by(Watchlist.created_at.desc()))
    watchlists = result.scalars().all()
    
    # Eager load entries
    outs = []
    for wl in watchlists:
        entries_q = select(WatchlistEntry).where(WatchlistEntry.watchlist_id == wl.id)
        entries = (await db.execute(entries_q)).scalars().all()
        outs.append(WatchlistOut(
            id=wl.id,
            name=wl.name,
            category=wl.category,
            description=wl.description,
            department=wl.department,
            is_active=wl.is_active,
            created_by=wl.created_by,
            created_at=wl.created_at,
            entries=[WatchlistEntryOut.model_validate(e) for e in entries]
        ))
    return outs


@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    wl_in: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "INVESTIGATOR"]))
):
    """Creates a new operational watchlist."""
    wl = Watchlist(
        name=wl_in.name,
        category=wl_in.category,
        description=wl_in.description,
        department=wl_in.department,
        is_active=wl_in.is_active,
        created_by=current_user.full_name
    )
    db.add(wl)
    await db.commit()
    await db.refresh(wl)
    return WatchlistOut(
        id=wl.id,
        name=wl.name,
        category=wl.category,
        description=wl.description,
        department=wl.department,
        is_active=wl.is_active,
        created_by=wl.created_by,
        created_at=wl.created_at,
        entries=[]
    )


@router.post("/{watchlist_id}/entries", response_model=WatchlistEntryOut, status_code=status.HTTP_201_CREATED)
async def add_watchlist_entry(
    watchlist_id: str,
    entry_in: WatchlistEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "INVESTIGATOR"]))
):
    """Adds a target license plate or entity to an active watchlist."""
    wl = (await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))).scalars().first()
    if not wl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")
    
    normalized = entry_in.identifier.upper().replace(" ", "").replace("-", "")
    entry = WatchlistEntry(
        watchlist_id=watchlist_id,
        entity_type=entry_in.entity_type,
        identifier=normalized,
        secondary_identifier=entry_in.secondary_identifier,
        threat_level=entry_in.threat_level,
        case_reference=entry_in.case_reference,
        notes=entry_in.notes,
        effective_from=entry_in.effective_from,
        expires_at=entry_in.expires_at,
        is_active=entry_in.is_active
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
