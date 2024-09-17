from django import forms
from .models import MedicalRecord

VACCINATION_CHOICES = [
    ('flu', 'Flu'),
    ('COVID', 'COVID')
]

VACCINATION_STATUS_CHOICES = [
    ('fully_vaccinated', 'Fully Vaccinated'),
    ('not_yet_vaccinated', 'Not Yet Vaccinated'),
    ('partially_vaccinated', 'Partially Vaccinated'),
    ('unknown', 'Unknown'),
]

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'date_of_birth',
            'allergies',
            'medical_conditions',
            'vaccinations',
            'vaccination_status',
            'last_checkup',
            'doctor_name',
            'doctor_contact',
            'doctor_email',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_checkup': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vaccinations': forms.Select(choices=MedicalRecord.VACCINATION_CHOICES, attrs={'class': 'form-control'}),
            'vaccination_status': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor_contact': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control'}),
            'doctor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'List any medical conditions or state "None"'}),
        }