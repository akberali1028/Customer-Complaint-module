from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://aivoa:aivoa@localhost:5432/aivoa")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ComplaintRecord(Base):
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fields: Mapped[dict] = mapped_column(JSON, nullable=False)
    risk_assessment: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


def save_complaint(fields: dict, risk_assessment: dict) -> int:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        record = ComplaintRecord(fields=fields, risk_assessment=risk_assessment)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.id
