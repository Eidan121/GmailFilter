import logging
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import SessionLocal
from app.models.account import GmailAccount
from app.scanner import flood_detector, notifier
from app.scanner.ai_suggester import generate_suggestions
from app.services.filter_service import get_cached_filter_criteria

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None
_is_running = False
_last_run: datetime | None = None
_next_run: datetime | None = None


def run_full_scan() -> None:
    global _is_running, _last_run
    if _is_running:
        logger.info("Scan already in progress, skipping.")
        return
    _is_running = True
    start = time.time()
    try:
        db = SessionLocal()
        accounts = db.query(GmailAccount).filter_by(is_active=True).all()
        for account in accounts:
            try:
                _scan_account(db, account)
            except Exception as e:
                logger.error("Scan failed for %s: %s", account.email, e)
        db.close()
    finally:
        _is_running = False
        _last_run = datetime.utcnow()
        logger.info("Full scan completed in %.1fs", time.time() - start)


def _scan_account(db, account: GmailAccount) -> None:
    logger.info("Scanning account %s", account.email)
    t0 = time.time()

    existing_addresses = get_cached_filter_criteria(account.id, db)
    candidates, total = flood_detector.detect(account.encrypted_token, existing_addresses)

    scan_result = notifier.persist_scan(
        db=db,
        account_id=account.id,
        emails_scanned=total,
        flood_count=len(candidates),
        duration_sec=time.time() - t0,
    )

    if not candidates:
        notifier.emit_event("scan_complete", {"account_id": account.id, "new_count": 0})
        return

    # Get existing labels for Claude context
    try:
        from app.services.label_service import list_labels
        labels = list_labels(account.encrypted_token)
        label_names = [l.name for l in labels]
    except Exception:
        label_names = []

    suggestions = generate_suggestions(candidates, label_names)
    new_count = 0
    for cand, suggestion in zip(candidates, suggestions):
        import json
        notifier.upsert_suggestion(
            db=db,
            account_id=account.id,
            scan_result_id=scan_result.id,
            sender_email=cand.sender_email,
            sender_domain=cand.sender_domain,
            email_count=cand.count,
            suggested_label=suggestion.get("suggested_label", "Bulk"),
            suggested_action=suggestion.get("suggested_action", "label"),
            criteria_json=json.dumps(suggestion.get("filter_criteria", {"from": cand.sender_email})),
            ai_rationale=suggestion.get("rationale"),
        )
        notifier.emit_event("suggestion_added", {
            "account_id": account.id,
            "sender_email": cand.sender_email,
            "email_count": cand.count,
        })
        new_count += 1

    notifier.emit_event("scan_complete", {"account_id": account.id, "new_count": new_count})
    logger.info("Account %s: %d flood senders, %d suggestions", account.email, len(candidates), new_count)


def start_scheduler() -> BackgroundScheduler:
    global _scheduler, _next_run
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_full_scan,
        trigger=IntervalTrigger(hours=settings.scan_interval_hours),
        id="flood_scan",
        replace_existing=True,
        next_run_time=datetime.utcnow(),
    )
    scheduler.start()
    _scheduler = scheduler
    job = scheduler.get_job("flood_scan")
    if job:
        _next_run = job.next_run_time
    return scheduler


def get_status() -> dict:
    job = _scheduler.get_job("flood_scan") if _scheduler else None
    return {
        "last_run": _last_run,
        "next_run": job.next_run_time if job else None,
        "is_running": _is_running,
    }


def start() -> None:
    """Entry point for: uv run python -m app.scanner.daemon"""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting scanner daemon (interval: %dh)", settings.scan_interval_hours)
    start_scheduler()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        if _scheduler:
            _scheduler.shutdown()


if __name__ == "__main__":
    start()
