# API Documentation

Base URL (local): `http://localhost:8000`

---

## 1. `POST /webhook/payments`

Receives a payment status webhook from a payment provider (Razorpay or
PayPal format), verifies its authenticity, deduplicates it, and stores it.

### Headers

| Header                 | Required | Description                                      |
|-------------------------|----------|---------------------------------------------------|
| `Content-Type`          | Yes      | Must be `application/json`                        |
| `X-Razorpay-Signature`  | Yes      | `hmac_sha256(secret="test_secret", body=raw_body)` hex digest |

### Request Body

Either a **Razorpay-style** payload:
```json
{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_004",
        "status": "captured",
        "amount": 4000,
        "currency": "INR"
      }
    }
  },
  "created_at": 1751886985,
  "id": "evt_cap_004"
}
```

or a **PayPal-style** payload:
```json
{
  "id": "WH-58D329510W468432W",
  "event_type": "PAYMENT.CAPTURE.COMPLETED",
  "resource": {
    "id": "3C679366NW443042N",
    "status": "COMPLETED"
  },
  "create_time": "2025-07-08T12:15:33.000Z"
}
```

### Responses

**`200 OK`** — event accepted and stored (or already existed):
```json
{
  "status": "ok",
  "message": "Event received and stored",
  "event_id": "evt_cap_004",
  "payment_id": "pay_004"
}
```
If the `event_id` had already been processed before, you'll instead get:
```json
{
  "status": "ok",
  "message": "Event already processed (duplicate ignored)",
  "event_id": "evt_cap_004",
  "payment_id": "pay_004"
}
```

**`403 Forbidden`** — signature missing or incorrect:
```json
{ "status": "error", "message": "Invalid or missing signature" }
```

**`400 Bad Request`** — body isn't valid JSON, or doesn't match a known
Razorpay/PayPal shape:
```json
{ "status": "error", "message": "Invalid JSON body" }
```
```json
{ "status": "error", "message": "Payload does not match a known Razorpay or PayPal webhook shape" }
```

### Example (curl)

```bash
SIG=$(python3 scripts/compute_signature.py mock_payloads/payment_authorized.json)

curl -X POST http://localhost:8000/webhook/payments \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $SIG" \
  -d @mock_payloads/payment_authorized.json
```

---

## 2. `GET /payments/{payment_id}/events`

Returns all stored events for a given `payment_id`, sorted chronologically
by the time our server received them (`received_at` ascending).

### Path Parameters

| Param        | Type   | Description                          |
|--------------|--------|---------------------------------------|
| `payment_id` | string | e.g. `pay_014`                        |

### Response — `200 OK`

```json
[
  {
    "event_type": "payment.authorized",
    "received_at": "2025-07-08T12:00:00Z"
  },
  {
    "event_type": "payment.captured",
    "received_at": "2025-07-08T12:01:23Z"
  }
]
```

If the `payment_id` has no recorded events, this returns an empty array
`[]` with a `200 OK` (not a 404) — it's a valid query that simply found
nothing yet, which is more convenient for clients polling for updates.

### Example (curl)

```bash
curl http://localhost:8000/payments/pay_014/events
```

---

## 3. `GET /health`

Simple liveness check.

### Response — `200 OK`
```json
{ "status": "healthy" }
```

---

## Error Handling Summary

| Scenario                              | Status Code | 
|-----------------------------------------|--------------|
| Missing `X-Razorpay-Signature` header   | 403          |
| Incorrect signature                     | 403          |
| Malformed JSON body                     | 400          |
| Valid JSON but unrecognized payload shape| 400         |
| Duplicate `event_id`                    | 200 (idempotent no-op) |
| Successful new event                    | 200          |
| Query for payment with no events        | 200 (empty list) |

## Interactive Docs

FastAPI auto-generates interactive Swagger UI and ReDoc documentation once
the server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
