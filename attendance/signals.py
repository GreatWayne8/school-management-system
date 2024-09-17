from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from .models import ClockInOut

@receiver(user_logged_in)
def auto_clock_in(sender, request, user, **kwargs):
    if user.is_teacher:
        today = timezone.now().date()
        # Check for existing clock-in record
        existing_clock_in = ClockInOut.objects.filter(
            user=user,
            date=today,
            clock_out_time__isnull=True
        ).exists()
        
        if not existing_clock_in:
            ClockInOut.objects.create(
                user=user,
                date=today,
                clock_in_time=timezone.now()
            )
