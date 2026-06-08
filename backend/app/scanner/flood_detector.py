import re
import time
from dataclasses import dataclass, field
from email.utils import parseaddr

from app.config import settings
from app.services.gmail_client import get_service


@dataclass
class FloodCandidate:
    sender_email: str
    sender_domain: str
    count: int
    sample_subjects: list[str] = field(default_factory=list)


def detect(encrypted_token: str | None, existing_filter_addresses: set[str]) -> tuple[list[FloodCandidate], int]:
    """
    Return (candidates, total_emails_scanned).
    Candidates are senders with count >= FLOOD_THRESHOLD not already in a filter.
    """
    svc = get_service(encrypted_token)
    sender_map: dict[str, dict] = {}
    total = 0
    page_token = None
    pages = 0

    while pages < 5:
        kwargs: dict = {"userId": "me", "q": "in:inbox -has:userlabels", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token
        result = svc.users().messages().list(**kwargs).execute()
        messages = result.get("messages", [])
        if not messages:
            break

        # Batch fetch headers in groups of 100
        for i in range(0, len(messages), 100):
            batch_ids = [m["id"] for m in messages[i : i + 100]]
            _fetch_headers_batch(svc, batch_ids, sender_map)

        total += len(messages)
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or total >= settings.max_messages_per_scan:
            break

    candidates: list[FloodCandidate] = []
    for sender_email, data in sender_map.items():
        if data["count"] < settings.flood_threshold:
            continue
        if sender_email.lower() in existing_filter_addresses:
            continue
        domain = _extract_domain(sender_email)
        candidates.append(FloodCandidate(
            sender_email=sender_email,
            sender_domain=domain,
            count=data["count"],
            sample_subjects=data["subjects"][:10],
        ))

    candidates.sort(key=lambda c: c.count, reverse=True)
    return candidates, total


def _fetch_headers_batch(svc, message_ids: list[str], sender_map: dict) -> None:
    # Use a simple loop with fields to minimize quota usage
    for msg_id in message_ids:
        try:
            msg = svc.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "Subject"],
            ).execute()
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            from_raw = headers.get("From", "")
            subject = headers.get("Subject", "(no subject)")
            _, addr = parseaddr(from_raw)
            if not addr:
                continue
            addr = addr.lower().strip()
            if addr not in sender_map:
                sender_map[addr] = {"count": 0, "subjects": []}
            sender_map[addr]["count"] += 1
            if len(sender_map[addr]["subjects"]) < 10:
                sender_map[addr]["subjects"].append(subject)
        except Exception:
            continue


def _extract_domain(email: str) -> str:
    match = re.search(r"@([\w.\-]+)", email)
    return match.group(1) if match else email
