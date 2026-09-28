from __future__ import annotations

from dataclasses import dataclass

from .infrai_sms import SmsClient, SmsReply


@dataclass(frozen=True)
class PaymentEvent:
    event_id: str
    recipient: str
    amount_cents: int
    approved: bool


def send_payment_notice(event: PaymentEvent, template_id: str, client: SmsClient) -> SmsReply | None:
    """Only approved payments produce a customer-facing SMS."""
    if not event.approved:
        return None
    return client.send(
        to=event.recipient,
        template_id=template_id,
        template_vars={"amount": f"{event.amount_cents / 100:.2f}", "event_id": event.event_id},
        request_id=f"payment-notice-{event.event_id}",
    )
