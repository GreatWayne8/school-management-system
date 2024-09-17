from django import forms
from .models import ClockInOut

class ClockInOutForm(forms.ModelForm):
    class Meta:
        model = ClockInOut
        fields = ['clock_in_time', 'clock_out_time']
