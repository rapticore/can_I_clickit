import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    tier = Column(String(20), nullable=False, default="free")
    grandma_mode = Column(Boolean, default=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    scans = relationship("ScanMetadata", back_populates="user")
    recovery_sessions = relationship("RecoverySession", back_populates="user")
    guardian_links = relationship(
        "FamilyLink",
        foreign_keys="FamilyLink.guardian_user_id",
        back_populates="guardian",
    )
    member_links = relationship(
        "FamilyLink",
        foreign_keys="FamilyLink.member_user_id",
        back_populates="member",
    )


class ScanMetadata(Base):
    __tablename__ = "scan_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    scan_type = Column(String(20), nullable=False)
    verdict = Column(String(20), nullable=False)
    confidence = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    scam_pattern = Column(String(100), nullable=True)
    analysis_tier = Column(String(20), nullable=False, default="fast_path")
    latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="scans")
    feedback = relationship("Feedback", back_populates="scan", uselist=False)


class URLCache(Base):
    __tablename__ = "url_cache"

    url_hash = Column(String(64), primary_key=True)
    verdict = Column(String(20), nullable=False)
    confidence = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RecoverySession(Base):
    __tablename__ = "recovery_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    steps_completed = Column(Integer, default=0)
    total_steps = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="recovery_sessions")


class FamilyLink(Base):
    __tablename__ = "family_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    guardian_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    member_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    guardian = relationship("User", foreign_keys=[guardian_user_id], back_populates="guardian_links")
    member = relationship("User", foreign_keys=[member_user_id], back_populates="member_links")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scan_metadata.id"), nullable=False, index=True)
    user_reported_verdict = Column(String(50), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    scan = relationship("ScanMetadata", back_populates="feedback")
