"""
Parses incoming webhook JSON into a normalized (event_type, event_id,
payment_id, status, provider) tuple.

Supports two real-world shapes, as required by the assignment
("Razorpay or PayPal format"):

Razorpay:
    {
      "event": "payment.captured",
      "payload": {"payment": {"entity": {"id": "pay_004", "status": "captured", ...}}},
      "created_at": 1751886985,
      "id": "evt_cap_004"
    }

PayPal:
    {
      "id": "WH-58D329510W468432W",
      "event_type": "PAYMENT.CAPTURE.COMPLETED",
      "resource": {"id": "3C679366NW443042N", "status": "COMPLETED", ...},
      "create_time": "2021-04-27T12:15:33.000Z"
    }

We distinguish the two formats by their distinguishing top-level keys:
Razorpay uses "event" + "payload", PayPal uses "event_type" + "resource".
"""

from dataclasses import dataclass
from typing import Optional


class UnrecognizedPayloadFormat(ValueError):
    """Raised when a JSON body doesn't match any known provider format."""


@dataclass
class ParsedEvent:
    event_id: str
    event_type: str
    payment_id: str
    status: Optional[str]
    provider: str


def parse_webhook_payload(payload: dict) -> ParsedEvent:
    if not isinstance(payload, dict):
        raise UnrecognizedPayloadFormat("Payload must be a JSON object")

    # --- Razorpay format ---
    if "event" in payload and "payload" in payload:
        try:
            entity = payload["payload"]["payment"]["entity"]
            return ParsedEvent(
                event_id=payload["id"],
                event_type=payload["event"],
                payment_id=entity["id"],
                status=entity.get("status"),
                provider="razorpay",
            )
        except (KeyError, TypeError) as exc:
            raise UnrecognizedPayloadFormat(
                f"Malformed Razorpay-style payload: missing {exc}"
            ) from exc

    # --- PayPal format ---
    if "event_type" in payload and "resource" in payload:
        try:
            resource = payload["resource"]
            return ParsedEvent(
                event_id=payload["id"],
                event_type=payload["event_type"],
                payment_id=resource["id"],
                status=resource.get("status"),
                provider="paypal",
            )
        except (KeyError, TypeError) as exc:
            raise UnrecognizedPayloadFormat(
                f"Malformed PayPal-style payload: missing {exc}"
            ) from exc

    raise UnrecognizedPayloadFormat(
        "Payload does not match a known Razorpay or PayPal webhook shape"
    )
