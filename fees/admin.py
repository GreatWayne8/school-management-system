from django.contrib import admin
from .models import FeeCategory, FeeStructure, Payment, PaymentReminder

admin.site.register(FeeCategory)
admin.site.register(FeeStructure)
admin.site.register(Payment)
admin.site.register(PaymentReminder)
