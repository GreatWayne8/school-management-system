from django.utils import timezone
from .models import Payment
from .views import send_payment_receipt

def handle_failed_payments():
    """
    Cron job to retry failed email receipts
    Should be scheduled to run periodically (e.g., every hour)
    """
    failed_payments = Payment.objects.filter(
        email_sent=False,
        email_attempts__lt=3,
        created_at__gte=timezone.now() - timezone.timedelta(days=3)  # Only recent failures
    )
    
    for payment in failed_payments:
        send_payment_receipt(payment) 