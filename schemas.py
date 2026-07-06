"""
Pydantic schemas — define the shape of API responses.
Keeping these separate from the ORM model (models.py) means our API's
public contract doesn't accidentally leak internal DB columns.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WebhookAcceptedResponse(BaseModel):
    status: str
    message: str
    event_id: Optional[str] = None
    payment_id: Optional[str] = None


class PaymentEventOut(BaseModel):
    event_type: str
    received_at: datetime

    class Config:
        from_attributes = True  # allows creation directly from ORM objects


class ErrorResponse(BaseModel):
    status: str
    message: str
