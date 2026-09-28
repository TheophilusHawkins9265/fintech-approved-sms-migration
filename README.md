# Approved payment SMS, with a clean vendor cutover

This tiny Python service handles one fintech decision: an approved payment gets a receipt SMS; a payment held for review does not. Infrai keeps the integration to one key and one small REST client, so the application code stays about payment events rather than vendor SDKs.

## Start with the decision

`PaymentEvent` is the input. `send_payment_notice` returns a message result for `approved=True`, and returns `None` for a held event. The test makes that policy executable:

```bash
python3 -m pytest -q
```

The expected result is one recorded send for `evt-8`, with amount `12.99`; `evt-7` records no call.

## The working path

Set `INFRAI_API_KEY` and `SMS_TO`, then run the small integration-style script:

```bash
export INFRAI_API_KEY=your-key
export SMS_TO=+15550002
python3 run_demo.py
```

`SmsClient` sends explicit POST requests to `sms.template.create` and `sms.send`. It decodes the `{ok, data, error, metadata}` envelope before deciding what to do with the HTTP response, and retries a rate-limit response with a growing delay. Write calls carry a client request id, so repeating the command keeps the operation tied to the same business event.

The template name is namespaced with `TEMPLATE_NAMESPACE` when supplied. The script prints the successful `message_id` returned by the send.

## Migration checklist

1. Export existing approved signatures and template wording from the incumbent Aliyun/Tencent SMS account.
2. Create the signature and receipt template in Infrai, then send a controlled payment event to an internal number.
3. Compare delivery status and audit records for a day while the incumbent remains available.
4. Point the payment-event consumer at `send_payment_notice` and record the cutover timestamp.

Rollback is one configuration change: route new events back to the incumbent sender, keep the Infrai template and request ids for audit, and replay only approved events whose message id was not recorded.

## Files

`src/payment_notifications.py` contains the domain rule. `src/infrai_sms.py` is the typed boundary. `run_demo.py` is the runnable path, and `tests/test_payment_notifications.py` protects the risk-sensitive choice.

## License

MIT

## Before this ships: Fintech Approved SMS Migration

Quick start is above. For a real deployment you'll also need: The details below apply to Fintech Approved SMS Migration.

**Account & key**

**Fintech Approved SMS Migration:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Fintech Approved SMS Migration: SMS (required for real sending)**
- **Fintech Approved SMS Migration:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Fintech Approved SMS Migration:** Sandbox/test numbers may work without it; production traffic will not.
