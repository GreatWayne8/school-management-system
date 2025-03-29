from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


class Student(models.Model):
    name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class FeeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class FeeStructure(models.Model):
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    term = models.CharField(max_length=20, default="3")

    def __str__(self):
        return f"{self.category.name} - {self.amount}"

class FeeStatement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student} - Balance: {self.balance}"


def get_default_payer():
    return User.objects.first().id if User.objects.exists() else None  # Set default to first user

class Payment(models.Model):
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments_made",
        default=get_default_payer  # Automatically assigns an existing user
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments_received")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Cash', 'Cash'), ('Card', 'Card'), ('Online', 'Online'), ('M-Pesa', 'M-Pesa')
    ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"), ("Completed", "Completed"), ("Failed", "Failed")
    ], default="Pending")

    def __str__(self):
        return f"{self.payer.username} paid for {self.student.name} - {self.amount_paid} - {self.status}"