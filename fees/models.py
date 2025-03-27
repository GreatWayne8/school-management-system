
from django.db import models
from django.conf import settings


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

    def __str__(self):
        return f"{self.category.name} - {self.amount}"

class FeeStatement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student} - Balance: {self.balance}"


class Payment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        return f"{self.student.username} - {self.amount_paid} - {self.status}"