import threading

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scan_result import ScanResult
from app.models.suggestion import FilterSuggestion
from app.scanner import daemon
from app.schemas.scan import ScanResultOut, ScanStatus

router = APIRouter()


@router.get("/status", response_model=ScanStatus)
def scan_status(db: Session = Depends(get_db)):
    status = daemon.get_status()
    pending = db.query(FilterSuggestion).filter_by(status="pending").count()
    return ScanStatus(
        last_run=status["last_run"],
        next_run=status["next_run"],
        pending_suggestions=pending,
        is_running=status["is_running"],
    )


@router.post("/trigger", status_code=202)
def trigger_scan():
    thread = threading.Thread(target=daemon.run_full_scan, daemon=True)
    thread.start()
    return {"detail": "Scan triggered"}


@router.get("/history", response_model=list[ScanResultOut])
def scan_history(db: Session = Depends(get_db)):
    return db.query(ScanResult).order_by(ScanResult.scanned_at.desc()).limit(20).all()
