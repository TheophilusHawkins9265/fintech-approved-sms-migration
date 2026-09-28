import os

from src.infrai_sms import SmsClient
from src.payment_notifications import PaymentEvent, send_payment_notice


def main() -> None:
    client = SmsClient()
    template = client.create_template(
        name=f"fintech-payment-receipt-{os.environ.get('TEMPLATE_NAMESPACE', 'local')}",
        body="Payment of {{amount}} approved ({{event_id}}).",
        request_id="template-fintech-payment-receipt",
    )
    template_id = str(template["id"])
    result = send_payment_notice(PaymentEvent("evt-demo", os.environ["SMS_TO"], 1299, True), template_id, client)
    print({"message_id": result.message_id if result else None})


if __name__ == "__main__":
    main()
