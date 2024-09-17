from django.db import models
from django.conf import settings

class Route(models.Model):
    route_name = models.CharField(max_length=100)
    description = models.TextField(default='No description available')
    start_location = models.CharField(max_length=255, default='Unknown start location')  
    end_location = models.CharField(max_length=255, default='Unknown end location')  

    def __str__(self):
        return self.route_name
    
class Bus(models.Model):
    bus_number = models.CharField(max_length=255, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_driver': True})
    capacity = models.PositiveIntegerField()
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, limit_choices_to={'is_teacher': True}, blank=True, related_name='buses')

    def __str__(self):
        return self.bus_number


class StudentPickup(models.Model):
    student = models.OneToOneField('accounts.Student', on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

    def __str__(self):
        student_name = str(self.student) if self.student else "No Student"
        route_name = str(self.route) if self.route else "No Route"
        return f"{student_name} - Route: {route_name}"


class TransportRequest(models.Model):
    TRANSPORT_CHOICES = [
        ('pickup', 'Pickup'),
        ('dropoff', 'Drop-off'),
        ('both', 'Both Pickup and Drop-off'),
    ]
    
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_CHOICES)
    pickup_time = models.DateTimeField(blank=True, null=True)
    pickup_location = models.CharField(max_length=255, blank=True, null=True)
    dropoff_time = models.DateTimeField(blank=True, null=True)
    dropoff_location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transport Request for {self.student} - {self.get_transport_type_display()}"