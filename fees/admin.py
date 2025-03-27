from django.contrib import admin
from .models import FeeCategory, FeeStructure, Payment,FeeStatement

admin.site.register(FeeCategory)
admin.site.register(FeeStructure)
admin.site.register(Payment)

@admin.register(FeeStatement)
class FeeStatementAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_due', 'amount_paid', 'balance')  # Adjust fields as needed
    search_fields = ('student__name',)  # Allow searching by student name
    list_filter = ('student',)