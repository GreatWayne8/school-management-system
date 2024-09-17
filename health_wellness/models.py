# models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User =get_user_model()

class MedicalRecord(models.Model):
    VACCINATION_CHOICES = [
        ('flu', 'Flu'),
        ('measles', 'Measles'),
        ('mumps', 'Mumps'),
        ('rubella', 'Rubella'),
        # Add more choices as needed
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    allergies = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    vaccinations = models.CharField(max_length=20, choices=VACCINATION_CHOICES, default='flu')  # Updated to CharField with choices
    vaccination_status = models.CharField(max_length=255, blank=True, null=True)
    last_checkup = models.DateField(blank=True, null=True)
    doctor_name = models.CharField(max_length=255, default='Unknown Doctor')  # Provide a default value
    doctor_contact = models.CharField(max_length=15, blank=True, null=True)
    doctor_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username}'s Medical Record"
    
class Student(models.Model):
    # Link to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wellness_student', default=1)  

    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Enrollment information
    enrollment_date = models.DateField()
    program = models.CharField(max_length=100)

    # Address
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class WellnessProgram(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, limit_choices_to={'is_student': True}, blank=True)

    def __str__(self):
        return self.name
