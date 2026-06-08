from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FilterSuggestion(Base):
    __tablename__ = "filter_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("gmail_accounts.id", ondelete="CASCADE"))
    scan_result_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("scan_results.id", ondelete="SET NULL"))
    sender_email: Mapped[str] = mapped_column(String, nullable=False)
    sender_domain: Mapped[str] = mapped_column(String, nullable=False)
    email_count: Mapped[int] = mapped_column(Integer, default=0)
    suggested_label: Mapped[str] = mapped_column(String, nullable=False)
    suggested_action: Mapped[str] = mapped_column(String, nullable=False)  # label | archive | label+archive
    criteria_json: Mapped[str] = mapped_column(String, nullable=False)
    ai_rationale: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending | accepted | dismissed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    acted_at: Mapped[datetime | None] = mapped_column(DateTime)
