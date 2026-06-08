from app.schemas.label import LabelCreate, LabelOut, LabelUpdate
from app.services.gmail_client import get_service


def list_labels(encrypted_token: str | None) -> list[LabelOut]:
    svc = get_service(encrypted_token)
    result = svc.users().labels().list(userId="me").execute()
    return [_to_out(l) for l in result.get("labels", [])]


def get_label(encrypted_token: str | None, label_id: str) -> LabelOut:
    svc = get_service(encrypted_token)
    label = svc.users().labels().get(userId="me", id=label_id).execute()
    return _to_out(label)


def create_label(encrypted_token: str | None, data: LabelCreate) -> LabelOut:
    svc = get_service(encrypted_token)
    body: dict = {
        "name": data.name,
        "labelListVisibility": data.label_list_visibility,
        "messageListVisibility": data.message_list_visibility,
    }
    if data.color:
        body["color"] = {k: v for k, v in {"textColor": data.color.text_color, "backgroundColor": data.color.background_color}.items() if v}
    created = svc.users().labels().create(userId="me", body=body).execute()
    return _to_out(created)


def update_label(encrypted_token: str | None, label_id: str, data: LabelUpdate) -> LabelOut:
    svc = get_service(encrypted_token)
    body: dict = {"id": label_id}
    if data.name is not None:
        body["name"] = data.name
    if data.color:
        body["color"] = {k: v for k, v in {"textColor": data.color.text_color, "backgroundColor": data.color.background_color}.items() if v}
    updated = svc.users().labels().update(userId="me", id=label_id, body=body).execute()
    return _to_out(updated)


def delete_label(encrypted_token: str | None, label_id: str) -> None:
    svc = get_service(encrypted_token)
    svc.users().labels().delete(userId="me", id=label_id).execute()


def _to_out(label: dict) -> LabelOut:
    return LabelOut(
        id=label["id"],
        name=label["name"],
        type=label.get("type"),
        messages_total=label.get("messagesTotal"),
        messages_unread=label.get("messagesUnread"),
        color=label.get("color"),
    )
