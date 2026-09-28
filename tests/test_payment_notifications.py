from src.payment_notifications import PaymentEvent, send_payment_notice


class RecordingClient:
    def __init__(self):
        self.calls = []

    def send(self, **kwargs):
        self.calls.append(kwargs)
        return "sent"


def test_risk_rule_sends_only_approved_payment():
    client = RecordingClient()
    assert send_payment_notice(PaymentEvent("evt-7", "+15550001", 1299, False), "tpl-1", client) is None
    assert client.calls == []
    result = send_payment_notice(PaymentEvent("evt-8", "+15550002", 1299, True), "tpl-1", client)
    assert result == "sent"
    assert client.calls[0]["template_vars"] == {"amount": "12.99", "event_id": "evt-8"}
    assert client.calls[0]["request_id"] == "payment-notice-evt-8"
