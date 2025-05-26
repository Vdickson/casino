from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from casino.models import Subscriber
import requests  # For SMS integration


class Command(BaseCommand):
    help = 'Send promotional messages to subscribers'

    def handle(self, *args, **options):
        # Email promotion
        subscribers = Subscriber.objects.filter(is_active=True)
        subject = "🎰 New Casino Promotions!"
        message = """Check out our latest offers:
        - 100% Signup Bonus
        - 30% Regular Bonus
        - 15% Cashback
        - 50% Referral Bonus

        Play now: [Your Website URL]"""

        # Send emails
        for sub in subscribers:
            if sub.email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [sub.email],
                    fail_silently=False
                )

        # Send SMS via Twilio (example)
        if hasattr(settings, 'TWILIO_API'):
            sms_body = "New casino bonuses! 100% Signup + 30% Regular Bonus! Reply STOP to opt out."
            for sub in subscribers.filter(phone__isnull=False):
                requests.post(
                    "https://api.twilio.com/2010-04-01/Accounts/ACXXXXXX/Messages.json",
                    auth=(settings.TWILIO_API['sid'], settings.TWILIO_API['token']),
                    data={
                        'To': sub.phone,
                        'From': settings.TWILIO_API['number'],
                        'Body': sms_body
                    }
                )