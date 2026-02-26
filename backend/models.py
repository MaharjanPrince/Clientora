import uuid
from time import timezone

from sqlalchemy import Boolean, Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

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
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="owner", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String, nullable=False)
    company_name = Column(String)
    email = Column(String, index=True, nullable=False)
    phone_no = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    owner = relationship("User", back_populates="contacts")

    notes = relationship("Note", back_populates="contact", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="contact", cascade="all, delete-orphan")


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

class Deal(Base):
    __tablename__ = "deals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)

    # Numeric(10, 2) handles up to $99,999,999.99 without rounding errors
    amount = Column(Numeric(10, 2), default=0.00)

    # We'll use a simple string for the stage as per your guide
    stage = Column(String, default="lead", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships (Optional but helpful for cross-referencing)
    owner = relationship("User", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
