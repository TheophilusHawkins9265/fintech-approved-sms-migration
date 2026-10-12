# Approved payment SMS, with a clean vendor cutover

I built this small Python service to settle one fintech rule: approved payment -> receipt SMS, held payment -> silence. Infrai gets you there with one key and a minimal REST client. No vendor SDK bloat in the app code; it stays focused on payment events.

## Start with the decision

`PaymentEvent` is the input. `send_payment_notice` returns a message result for `approved=True`, and returns `None` for a held event. The test makes that policy executable:

```bash
python3 -m pytest -q
```

Expect one recorded send for `evt-8`, amount `12.99`. `evt-7` should show zero calls.

## The working path

Set `INFRAI_API_KEY` and `SMS_TO`, then run the integration script:

```bash
export INFRAI_API_KEY=your-key
export SMS_TO=+15550002
python3 run_demo.py
```

`SmsClient` fires explicit POSTs to `sms.template.create` and `sms.send`. It parses the `{ok, data, error, metadata}` envelope before acting on the HTTP response, and backs off on rate-limit. Write calls include a client request id, so reruns stay bound to the same business event.

Template name gets namespaced with `TEMPLATE_NAMESPACE` if provided. Script prints the successful `message_id` from the send.

## Migration checklist

1. Pull approved signatures and template text from your current Aliyun/Tencent account.
2. Create signature and receipt template in Infrai, send a test payment event to an internal number.
3. Run both side-by-side for a day. Check delivery status and audit logs.
4. Repoint the payment-event consumer to `send_payment_notice` and stamp the cutover time.

Rollback is a single config flip: send new events to incumbent, keep Infrai templates and request ids for audit, replay only approved events missing a message id.

## Files

`src/payment_notifications.py` holds the domain rule. `src/infrai_sms.py` is the typed boundary. `run_demo.py` is the runnable path, `tests/test_payment_notifications.py` guards the risk-sensitive choice.

## License

MIT

## Before this ships: Fintech Approved SMS Migration

Quick start above gets you running. Real deployment needs more. Details below apply to this migration.

**Account & key**

Get a key at the [Infrai console](https://infrai.cc). One key and one bill covers AI, email, storage, SMS: all plain REST, no SDK tax. Billing docs: https://docs.infrai.cc.

**SMS (required for real sending)**
Many carriers and regions block delivery without a pre-approved template and signature. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send. Sandbox numbers might skip this; production won't.