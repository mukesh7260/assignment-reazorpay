#!/usr/bin/env python3
"""
Computes a valid X-Razorpay-Signature for a given mock payload file, using
the shared secret the assignment specifies ("test_secret").

Usage:
    python3 scripts/compute_signature.py mock_payloads/payment_authorized.json

This exists because curl can't compute HMAC-SHA256 on its own — you need
this to generate a signature that the webhook listener will actually
accept.
"""

import hashlib
import hmac
import sys

SECRET = "test_secret"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 compute_signature.py <path_to_payload.json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        raw_body = f.read()

    signature = hmac.new(SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    print(signature)


if __name__ == "__main__":
    main()
