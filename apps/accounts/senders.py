from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.conf import settings
import threading
from apps.accounts.models import User


class EmailThread(threading.Thread):
    def __init__(self, email: EmailMessage):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class EmailUtil:
    @staticmethod
    def send_welcome_email(request: HttpRequest, user: User):
        current_site = f"{request.scheme}://{request.get_host()}"
        subject = "Account Verified"
        message = render_to_string(
            "accounts/welcome.html",
            {
                "domain": current_site,
                "name": f"{user.first_name} {user.last_name}",
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def send_payment_failed_email(request: HttpRequest, name, email, amount):
        if not email:
            return
        current_site = f"{request.scheme}://{request.get_host()}"
        subject = "Payment Unverified"
        message = render_to_string(
            "shop/payment_failed_email.html",
            {
                "domain": current_site,
                "name": name,
                "amount": amount,
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    def send_payment_success_email(request: HttpRequest, name, email, amount):
        if not email:
            return
        current_site = f"{request.scheme}://{request.get_host()}"
        subject = "Payment Verified"
        message = render_to_string(
            "shop/payment_success_email.html",
            {
                "domain": current_site,
                "name": name,
                "amount": amount,
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
