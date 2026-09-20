import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_owner
from app.models.court import Court
from app.schemas.court import CourtCreate, CourtOut

router = APIRouter(prefix="/courts", tags=["courts"])


@router.get("", response_model=list[CourtOut])
def list_courts(db: Session = Depends(get_db)):
    return db.query(Court).filter(Court.is_active.is_(True)).all()


@router.get("/{court_id}", response_model=CourtOut)
def get_court(court_id: uuid.UUID, db: Session = Depends(get_db)):
    court = db.get(Court, court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")
    return court


@router.post("", response_model=CourtOut, status_code=201)
def create_court(
    payload: CourtCreate,
    db: Session = Depends(get_db),
    _owner=Depends(get_current_owner), 
):
    court = Court(**payload.model_dump())
    db.add(court)
    db.commit()
    db.refresh(court)
    return court