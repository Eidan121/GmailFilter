import json
import logging

import anthropic

from app.config import settings
from app.scanner.flood_detector import FloodCandidate

logger = logging.getLogger(__name__)

_TOOL = {
    "name": "create_filter_suggestions",
    "description": "Create Gmail filter suggestions for flooding senders",
    "input_schema": {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sender_email": {"type": "string"},
                        "suggested_label": {"type": "string", "description": "Label name to apply"},
                        "suggested_action": {
                            "type": "string",
                            "enum": ["label", "archive", "label+archive"],
                        },
                        "filter_criteria": {
                            "type": "object",
                            "properties": {"from": {"type": "string"}},
                            "required": ["from"],
                        },
                        "rationale": {"type": "string", "description": "One sentence explanation"},
                    },
                    "required": ["sender_email", "suggested_label", "suggested_action", "filter_criteria", "rationale"],
                },
            }
        },
        "required": ["suggestions"],
    },
}


def generate_suggestions(
    candidates: list[FloodCandidate],
    existing_label_names: list[str],
) -> list[dict]:
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set — using heuristic suggestions")
        return _heuristic_suggestions(candidates)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    candidates_text = "\n".join(
        f"- {c.sender_email} ({c.count} emails)\n  Subjects: {'; '.join(c.sample_subjects[:5])}"
        for c in candidates
    )
    labels_text = ", ".join(existing_label_names) if existing_label_names else "none yet"

    prompt = f"""You are helping a user organize their Gmail inbox by creating filters for senders that are flooding their inbox with unlabeled emails.

Existing labels: {labels_text}

Flooding senders (unfiltered emails in inbox):
{candidates_text}

For each sender, suggest:
1. A label name (reuse an existing label if it fits, otherwise create a descriptive new one)
2. An action: "label" (just label), "archive" (skip inbox), or "label+archive" (label and skip inbox)
3. The filter criteria (use the sender email as the "from" value)
4. A one-sentence rationale

Prefer "label+archive" for newsletters and bulk mail. Prefer "label" for services the user actively uses."""

    try:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=4096,
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "create_filter_suggestions"},
            messages=[{"role": "user", "content": prompt}],
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == "create_filter_suggestions":
                return block.input.get("suggestions", [])
    except Exception as e:
        logger.error("Claude API error: %s", e)

    return _heuristic_suggestions(candidates)


def _heuristic_suggestions(candidates: list[FloodCandidate]) -> list[dict]:
    """Fallback when Claude API is unavailable."""
    results = []
    for c in candidates:
        domain = c.sender_domain
        label = _domain_to_label(domain)
        results.append({
            "sender_email": c.sender_email,
            "suggested_label": label,
            "suggested_action": "label+archive",
            "filter_criteria": {"from": c.sender_email},
            "rationale": f"Bulk sender with {c.count} unfiltered emails.",
        })
    return results


def _domain_to_label(domain: str) -> str:
    keywords = {
        "news": "News", "newsletter": "Newsletter", "promo": "Promotions",
        "marketing": "Marketing", "noreply": "Bulk", "notify": "Notifications",
        "notification": "Notifications", "update": "Updates", "info": "Info",
    }
    low = domain.lower()
    for kw, label in keywords.items():
        if kw in low:
            return label
    parts = domain.split(".")
    return parts[0].capitalize() if parts else "Bulk"
