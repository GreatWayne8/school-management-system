from django import forms
from .models import Bus, Route, StudentPickup
from accounts.models import User
from .models import TransportRequest



class BusForm(forms.ModelForm):
    driver = forms.ModelChoiceField(
        queryset=User.objects.filter(is_driver=True),
        required=True,
        label="Driver"
    )
    teachers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Teachers"
    )
    
    class Meta:
        model = Bus
        fields = ['bus_number', 'route', 'driver', 'capacity', 'teachers']


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_name', 'description', 'start_location', 'end_location']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter route name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter route description'}),
            'start_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter start location'}),
            'end_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter end location'}),
        }
        
class StudentPickupForm(forms.ModelForm):
    class Meta:
        model = StudentPickup
        fields = ['student', 'pickup_location', 'dropoff_location', 'route', 'bus']

class TransportRequestForm(forms.ModelForm):
    class Meta:
        model = TransportRequest
        fields = ['student', 'transport_type', 'pickup_time', 'pickup_location', 'dropoff_time', 'dropoff_location', 'notes']
        widgets = {
            'pickup_time': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Select Pickup Date and Time'}),
            'dropoff_time': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Select Dropoff Date and Time'}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Pickup Location'}),
            'dropoff_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Dropoff Location'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional Notes'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transport_type = cleaned_data.get('transport_type')

        if transport_type in ['pickup', 'both'] and not cleaned_data.get('pickup_time'):
            self.add_error('pickup_time', 'Pickup time is required for pickup or both transport types.')
        
        if transport_type in ['dropoff', 'both'] and not cleaned_data.get('dropoff_time'):
            self.add_error('dropoff_time', 'Drop-off time is required for drop-off or both transport types.')

        return cleaned_data