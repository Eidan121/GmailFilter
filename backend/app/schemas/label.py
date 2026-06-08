from pydantic import BaseModel


class LabelColor(BaseModel):
    text_color: str | None = None
    background_color: str | None = None


class LabelCreate(BaseModel):
    name: str
    label_list_visibility: str = "labelShow"
    message_list_visibility: str = "show"
    color: LabelColor | None = None


class LabelUpdate(BaseModel):
    name: str | None = None
    color: LabelColor | None = None


class LabelOut(BaseModel):
    id: str
    name: str
    type: str | None = None
    messages_total: int | None = None
    messages_unread: int | None = None
    color: dict | None = None
