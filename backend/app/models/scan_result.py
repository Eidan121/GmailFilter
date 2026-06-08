from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("gmail_accounts.id", ondelete="CASCADE"))
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    emails_scanned: Mapped[int] = mapped_column(Integer, default=0)
    flood_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0)
