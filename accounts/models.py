from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db.models import Q
from PIL import Image
from course.models import Program
from .validators import ASCIIUsernameValidator

LEVEL = (
    ("Kindergarten", "Kindergarten"),
    ("Primary", "Primary"),
    ("Junior Secondary", "Junior Secondary"),
)

RELATION_SHIP = (
    ("Father", "Father"),
    ("Mother", "Mother"),
    ("Brother", "Brother"),
    ("Sister", "Sister"),
    ("Grandmother", "Grandmother"),
    ("Grandfather", "Grandfather"),
    ("Other", "Other"),
)

GENDERS = (("M", "Male"), ("F", "Female"))

class CustomUserManager(UserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_office_assistant = models.BooleanField(default=False)
    is_lab_assistant = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True
    )
    email = models.EmailField(blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    def get_full_name(self):  # FIXED: Now it's a method
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.picture.path)
        except:
            pass

class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            qs = qs.filter(
                Q(student__first_name__icontains=query) |
                Q(student__last_name__icontains=query) |
                Q(student__username__icontains=query) |
                Q(student__email__icontains=query) |
                Q(level__icontains=query)
            ).distinct()
        return qs

class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_student')
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self): 
        return self.student.get_full_name()

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    relation_ship = models.CharField(max_length=20, choices=RELATION_SHIP, blank=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return f"{self.user.get_full_name()} (Specialization: {self.specialization})"

class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return str(self.user)
