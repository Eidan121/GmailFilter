from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CachedFilter(Base):
    __tablename__ = "cached_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("gmail_accounts.id", ondelete="CASCADE"))
    gmail_filter_id: Mapped[str] = mapped_column(String, nullable=False)
    criteria_json: Mapped[str] = mapped_column(String, nullable=False)
    action_json: Mapped[str] = mapped_column(String, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
