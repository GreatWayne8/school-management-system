from django import forms
from .models import Payment, FeeStructure, AcademicYear
from .models import Payment, Student
from accounts.models import Parent 

from django.contrib.auth import get_user_model


User = get_user_model()


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data



class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = '__all__'
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'late_fine': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'fee_structure', 'amount_paid', 'payment_method']
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user.is_staff or user.is_teacher:  # Admin or teacher view
            self.fields['student'].queryset = Student.objects.all()
            self.fields['student'].label = "Select Student"
            self.fields['student'].widget.attrs.update({
                'class': 'form-select select2',
                'placeholder': 'Search for student...'
            })
        elif user.is_parent:  # Parent view
            try:
                parent = Parent.objects.get(user=user)
                self.fields['student'].queryset = Student.objects.filter(id=parent.student.id)
                self.fields['student'].initial = parent.student
                self.fields['student'].widget = forms.HiddenInput()
            except Parent.DoesNotExist:
                self.fields['student'].queryset = Student.objects.none()
                self.fields['student'].help_text = "No student associated with your account"