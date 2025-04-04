from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum

User = get_user_model()

def get_default_payer():
    return User.objects.first().id if User.objects.exists() else None

class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=20, unique=True)
    current_class = models.CharField(max_length=50, blank=True, null=True)
    date_joined = models.DateField(null=True, blank=True)  

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.name} ({self.admission_number})"

class FeeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=True)
    code = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        verbose_name = "Fee Category"
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return self.name

class FeeStructure(models.Model):
    TERM_CHOICES = [
        ("1", "Term 1"), 
        ("2", "Term 2"), 
        ("3", "Term 3")
    ]
    
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    term = models.CharField(max_length=20, choices=TERM_CHOICES, default="1")
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE,
        null=True,  # Temporary
        blank=True
        )    
    late_fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('category', 'term', 'academic_year')
        ordering = ['academic_year', 'term', 'category']
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"

    def __str__(self):
        return f"{self.category.name} - {self.amount} (Term {self.term})"

class FeeStatement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_statements")
    fee_structure = models.ForeignKey(
        FeeStructure, 
        on_delete=models.CASCADE,
        null=True,  # Temporary allow null for migration
        blank=True  # Allow blank in forms
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    is_overdue = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'fee_structure')
        ordering = ['-last_updated']
        verbose_name = "Fee Statement"
        verbose_name_plural = "Fee Statements"

    def update_balance(self):
        # Handle cases where fee_structure might be null during migration
        if not self.fee_structure:
            return
            
        total_paid = Payment.objects.filter(
            student=self.student,
            fee_structure=self.fee_structure,
            status="Completed"
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        self.amount_paid = total_paid
        self.balance = self.amount_due - self.amount_paid
        self.is_overdue = timezone.now().date() > self.fee_structure.due_date and self.balance > 0
        self.save()

    def __str__(self):
        if not self.fee_structure:
            return f"{self.student.name} - No Fee Structure (Balance: {self.balance})"
        return f"{self.student.name} - {self.fee_structure} (Balance: {self.balance})"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'), 
        ('Card', 'Card'),
        ('Online', 'Online'), 
        ('M-Pesa', 'M-Pesa'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS = [
        ("Pending", "Pending"), 
        ("Completed", "Completed"), 
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments_made",
        default=get_default_payer
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name_plural = "Payments"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"REC-{self.student.admission_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
        
        # Update related fee statement
        statement, created = FeeStatement.objects.get_or_create(
            student=self.student,
            fee_structure=self.fee_structure,
            defaults={'amount_due': self.fee_structure.amount}
        )
        if not created:
            statement.amount_due = self.fee_structure.amount
        statement.update_balance()

    def __str__(self):
        return f"Payment #{self.receipt_number} - {self.student.name} ({self.amount_paid})"