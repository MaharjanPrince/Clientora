import uuid
from time import timezone

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # hash pw not actual
    hashed_password = Column(String, nullable=False)

    # Automatic Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
    is_active = Column(Boolean, default=True)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String, nullable=False)
    company_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_no = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
    notes = relationship("Note", back_populates="contact", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    content = Column(String(5000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Linking the note to a specific contact
    contact_id = Column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE")
    )
    contact = relationship("Contact", back_populates="notes")
