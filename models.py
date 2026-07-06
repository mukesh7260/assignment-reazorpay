"""
ORM model for persisted payment webhook events.

One row = one successfully-verified, successfully-parsed webhook event.
`event_id` has a UNIQUE constraint — this is what makes idempotency
enforceable at the database level, not just in application logic (so even
concurrent duplicate requests can't both slip through).
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, index=True)

    # Unique ID of the *event* itself, as sent by the provider
    # (e.g. "evt_auth_014"). Used for deduplication.
    event_id = Column(String, unique=True, nullable=False, index=True)

    # e.g. "payment.authorized", "payment.captured", "payment.failed"
    event_type = Column(String, nullable=False)

    # ID of the *payment* this event refers to (e.g. "pay_014").
    # Indexed because we query heavily by this field.
    payment_id = Column(String, nullable=False, index=True)

    # Normalized payment status extracted from the payload, e.g. "captured"
    status = Column(String, nullable=True)

    # Which provider format this came in as: "razorpay" or "paypal"
    provider = Column(String, nullable=False)

    # Full original JSON payload, stored verbatim for audit/debugging
    raw_payload = Column(Text, nullable=False)

    # When *our server* received and stored this event (server time,
    # not the provider's `created_at`) — this is what the assignment's
    # GET endpoint sorts by.
    received_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
