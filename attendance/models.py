from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class ClockInOut(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user} - {self.date}"

    @property
    def is_clocked_in(self):
        return self.clock_in_time is not None and self.clock_out_time is None

    @property
    def is_clocked_out(self):
        return self.clock_out_time is not None

    @property
    def duration(self):
        if self.clock_in_time and self.clock_out_time:
            return self.clock_out_time - self.clock_in_time
        return None

    def clean(self):
        if self.clock_in_time and self.clock_out_time and self.clock_out_time < self.clock_in_time:
            raise ValidationError("Clock-out time cannot be earlier than clock-in time")
        super().clean()

