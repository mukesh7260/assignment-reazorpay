#!/usr/bin/env bash
#
# End-to-end test script for the webhook listener.
# Run the server first in another terminal:
#     uvicorn app.main:app --reload --port 8000
#
# Then run this script:
#     bash scripts/test_webhook.sh
#
set -e

BASE_URL="http://localhost:8000"

sig() {
  python3 scripts/compute_signature.py "$1"
}

echo "== 1. Health check =="
curl -s "$BASE_URL/health"
echo -e "\n"

echo "== 2. Valid webhook: payment_authorized (pay_014) =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/payment_authorized.json)" \
  -d @mock_payloads/payment_authorized.json
echo -e "\n"

echo "== 3. Valid webhook: payment_captured for the same payment (pay_014) =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/payment_captured_pay014.json)" \
  -d @mock_payloads/payment_captured_pay014.json
echo -e "\n"

echo "== 4. Valid webhook: payment_captured (pay_004) =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/payment_captured.json)" \
  -d @mock_payloads/payment_captured.json
echo -e "\n"

echo "== 5. Valid webhook: payment_failed (pay_001) =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/payment_failed.json)" \
  -d @mock_payloads/payment_failed.json
echo -e "\n"

echo "== 6. PayPal-format webhook =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/paypal_payment_completed.json)" \
  -d @mock_payloads/paypal_payment_completed.json
echo -e "\n"

echo "== 7. DUPLICATE: re-send payment_authorized (same event_id) -> should say 'already processed', not create a 2nd row =="
curl -s -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $(sig mock_payloads/payment_authorized.json)" \
  -d @mock_payloads/payment_authorized.json
echo -e "\n"

echo "== 8. INVALID SIGNATURE -> should return 403 Forbidden =="
curl -s -i -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: TEST_SIGNATURE" \
  -d @mock_payloads/payment_authorized.json | head -n 1
echo -e "\n"

echo "== 9. MISSING SIGNATURE HEADER -> should return 403 Forbidden =="
curl -s -i -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -d @mock_payloads/payment_authorized.json | head -n 1
echo -e "\n"

echo "== 10. MALFORMED JSON -> should return 400 Bad Request =="
curl -s -i -X POST "$BASE_URL/webhook/payments" \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: irrelevant_since_body_is_broken" \
  -d '{not valid json' | head -n 1
echo -e "\n"

echo "== 11. Fetch full event history for pay_014 (should show authorized then captured, in order) =="
curl -s "$BASE_URL/payments/pay_014/events"
echo -e "\n"

echo "== 12. Fetch events for a payment_id with no events -> should return empty list =="
curl -s "$BASE_URL/payments/pay_does_not_exist/events"
echo -e "\n"

echo "All tests complete."
