"""
Simulated webhook signature verification.

Per the assignment spec:

    Shared secret: "test_secret"
    expected_signature = hmac_sha256(secret="test_secret", body=raw_payload)
    Header: X-Razorpay-Signature

The signature must be verified against the RAW request bytes (not a
re-parsed/re-serialized JSON object), because re-serialization can change
key order or whitespace and silently break a legitimate signature.

We use `hmac.compare_digest` for the comparison instead of `==` to avoid
leaking timing information that could help an attacker guess a valid
signature byte-by-byte.
"""

import hashlib
import hmac
import os

# In a real system this would come from a secrets manager / env var and
# would differ per-provider/per-merchant. Hardcoded here only because the
# assignment explicitly specifies this exact shared secret for testing.
WEBHOOK_SHARED_SECRET = os.environ.get("WEBHOOK_SHARED_SECRET", "test_secret")

SIGNATURE_HEADER = "X-Razorpay-Signature"


def compute_signature(raw_body: bytes, secret: str = WEBHOOK_SHARED_SECRET) -> str:
    """Compute the expected HMAC-SHA256 hex digest for a raw request body."""
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()


def is_valid_signature(raw_body: bytes, received_signature: str) -> bool:
    """
    Returns True only if `received_signature` is a non-empty string that
    matches the HMAC-SHA256 of `raw_body` computed with the shared secret.
    """
    if not received_signature:
        return False

    expected_signature = compute_signature(raw_body)
    return hmac.compare_digest(expected_signature, received_signature)
