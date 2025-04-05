from django.contrib import admin
from .models import FeeCategory, FeeStructure, Payment,FeeStatement
from.views import send_payment_receipt

admin.site.register(FeeCategory)
admin.site.register(FeeStructure)
admin.site.register(Payment)

@admin.register(FeeStatement)
class FeeStatementAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_due', 'amount_paid', 'balance')  # Adjust fields as needed
    search_fields = ('student__name',)  # Allow searching by student name
    list_filter = ('student',)

@admin.action(description='Resend payment receipts')
def resend_receipts(modeladmin, request, queryset):
    for payment in queryset:
        send_payment_receipt(payment)