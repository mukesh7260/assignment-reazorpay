# Payment Webhook Listener

A minimal, secure webhook listener built with **FastAPI** that accepts
mocked payment status updates (Razorpay or PayPal format), verifies
authenticity via a shared-secret HMAC signature, deduplicates and stores
events, and exposes an API to fetch a payment's event history.

## Tech Stack

- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM (SQLite by default, Postgres-ready)
- **Uvicorn** — ASGI server
- **Pydantic** — request/response validation

## Project Structure

```
payment-webhook-system/
├── app/
│   ├── main.py            # FastAPI app & route handlers
│   ├── database.py        # DB engine/session setup
│   ├── models.py          # SQLAlchemy ORM model
│   ├── schemas.py         # Pydantic response schemas
│   ├── security.py        # HMAC signature verification
│   └── payload_parser.py  # Razorpay/PayPal payload parsing
├── mock_payloads/          # Sample webhook payloads for testing
├── scripts/
│   ├── compute_signature.py  # Computes a valid signature for any payload file
│   └── test_webhook.sh       # End-to-end curl test script
├── requirements.txt
├── README.md
└── DOCS.md                # API documentation
```

## Setup (Local)

**1. Clone the repo and create a virtual environment:**
```bash
git clone <your-repo-url>
cd payment-webhook-system
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. (Optional) Configure environment variables:**
```bash
export WEBHOOK_SHARED_SECRET="test_secret"     # defaults to "test_secret" if unset
export DATABASE_URL="sqlite:///./payments.db"  # defaults to local SQLite file
```
To use PostgreSQL instead, just point `DATABASE_URL` at it, e.g.:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/webhooks"
```
(and `pip install psycopg2-binary` for the Postgres driver.)

**4. Run the server:**
```bash
uvicorn app.main:app --reload --port 8000
```
The API is now live at `http://localhost:8000`.
Interactive Swagger docs are auto-generated at `http://localhost:8000/docs`.

## Testing It

The shared secret is **`test_secret`**. Since curl can't compute an
HMAC on its own, use the included helper to generate a valid signature
for any payload file:

```bash
python3 scripts/compute_signature.py mock_payloads/payment_authorized.json
```

Then send the webhook with that signature:
```bash
curl -X POST http://localhost:8000/webhook/payments \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: <paste signature here>" \
  -d @mock_payloads/payment_authorized.json
```

Fetch the event history for that payment:
```bash
curl http://localhost:8000/payments/pay_014/events
```

**Or just run the full automated test suite in one go**
(covers: valid events, duplicate handling, invalid signature, missing
signature, malformed JSON, and history lookups):
```bash
bash scripts/test_webhook.sh
```

## Design Notes

- **Signature verification happens against the raw request bytes**, before
  any JSON parsing — re-serializing JSON can silently change whitespace/key
  order and break a legitimate signature, so we never do that before
  verifying.
- **`hmac.compare_digest`** is used instead of `==` to avoid timing attacks.
- **Idempotency** is enforced both in application logic (checked before
  insert) and at the database level (`event_id` has a `UNIQUE` constraint),
  so it's safe even if two duplicate requests arrive concurrently.
- **Both Razorpay and PayPal payload shapes** are supported via a small
  format-detection layer (`app/payload_parser.py`), satisfying the spec's
  "Razorpay or PayPal format" requirement.
- **`received_at`** (server-side timestamp) — not the provider's
  `created_at` — is what the history endpoint sorts by, since that's the
  authoritative record of when *we* saw the event.
- Storing the full raw payload (not just the extracted fields) preserves
  an audit trail and makes debugging/replaying events possible later.
