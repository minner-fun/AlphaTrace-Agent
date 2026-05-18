from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentJob(Base):
    __tablename__ = "agent_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chain_job_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    client_address: Mapped[str] = mapped_column(String(128))
    provider_address: Mapped[str] = mapped_column(String(128))
    evaluator_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="open")
    budget: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

