import smtplib
from email.message import EmailMessage
from app.core.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="send_order_email", bind=True, max_retries=3)
def send_order_confirmation_email(
    self,
    order_id: int,
    customer_email: str
):
    # Fetch credentials directly from environment variables
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.SENDER_PASSWORD
    if not sender_email or not sender_password:
        print("Missing email credentials in .env!")
        return {"status": "failed", "reason": "Missing credentials"}

    # Construct the beautiful email
    msg = EmailMessage()
    msg['Subject'] = f'Order Confirmation #{order_id}'
    msg['From'] = sender_email
    msg['To'] = customer_email

    msg.set_content(
        f"Thank you for your purchase!\n\n"
        f"""Your order #{order_id} has been received and
        is currently being processed.\n"""
        f"We will notify you once it ships.\n\n"
        f"Thanks,\nThe E-Commerce Team"
    )
    try:
        # Connect to the server and send
        print(f"Connecting to SMTP server to email {customer_email}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Real email successfully sent to {customer_email}!")
        return {"status": "success", "order_id": order_id}
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
