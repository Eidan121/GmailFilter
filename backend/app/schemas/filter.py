from pydantic import BaseModel


class FilterCriteria(BaseModel):
    from_: str | None = None
    to: str | None = None
    subject: str | None = None
    query: str | None = None
    has_attachment: bool | None = None
    exclude_chats: bool | None = None


class FilterAction(BaseModel):
    add_label_ids: list[str] = []
    remove_label_ids: list[str] = []
    forward: str | None = None


class FilterCreate(BaseModel):
    criteria: FilterCriteria
    action: FilterAction


class FilterOut(BaseModel):
    id: str
    criteria: dict
    action: dict
