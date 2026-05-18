from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chain_job_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    report_json: Mapped[str] = mapped_column(Text)
    report_hash: Mapped[str] = mapped_column(String(128), index=True)
    report_uri: Mapped[str | None] = mapped_column(String(512), nullable=True)
    submit_tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

