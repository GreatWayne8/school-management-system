from django.contrib import admin
from .models import MedicalRecord, WellnessProgram

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'vaccination_status', 'last_checkup', 'doctor_name', 'doctor_contact')
    search_fields = ('student__username', 'doctor_name', 'doctor_contact')

@admin.register(WellnessProgram)
class WellnessProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name', 'description')
