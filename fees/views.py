from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FeeStructure, Payment
from .forms import FeeStructureForm, PaymentForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Check if user is admin
def is_admin(user):
    return user.is_staff

# ---------------------------- #
# 1. FEE STRUCTURE MANAGEMENT (CRUD)
# ---------------------------- #

@login_required
@user_passes_test(is_admin)
def create_fee_structure(request):
    """Admin can create a new fee structure."""
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fees:fee_structure_list')  
    else:
        form = FeeStructureForm()

    return render(request, 'fees/create_fee_structure.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_fee_structure(request, fee_id):
    """Admin can edit an existing fee structure."""
    fee = get_object_or_404(FeeStructure, id=fee_id)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            return redirect('fees:fee_structure_list')
    else:
        form = FeeStructureForm(instance=fee)
    
    return render(request, 'fees/edit_fee_structure.html', {'form': form, 'fee': fee})

@login_required
@user_passes_test(is_admin)
def delete_fee_structure(request, fee_id):
    """Admin can delete a fee structure."""
    fee = get_object_or_404(FeeStructure, id=fee_id)
    if request.method == 'POST':
        fee.delete()
        return redirect('fees:fee_structure_list')
    
    return render(request, 'fees/confirm_delete.html', {'fee': fee})

@login_required
def fee_structure_list(request):
    """List all fee structures (visible to all users)."""
    fee_structures = FeeStructure.objects.all()
    return render(request, 'fees/fee_structure_list.html', {'fee_structures': fee_structures})

# ---------------------------- #
# 2. FEE PAYMENT MANAGEMENT
# ---------------------------- #

@login_required
def payment_list(request):
    """Admin sees all payments, students/parents see their own payments."""
    if request.user.is_staff:
        payments = Payment.objects.all()  # Admin sees all payments
    elif request.user.role in ['parent', 'teacher']:
        payments = Payment.objects.filter(payer=request.user)  # See payments made
    else:
        payments = Payment.objects.filter(student=request.user)  # See payments received

    return render(request, 'fees/payment_list.html', {'payments': payments})


@login_required
def generate_receipt(request, payment_id):
    """Generate receipt for a specific payment."""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, 'fees/receipt.html', {'payment': payment})

@login_required
def fee_payment_view(request):
    """Show payment form with a dropdown of students (for admins)."""
    if request.user.is_staff:
        students = User.objects.filter(is_staff=False)
    else:
        students = None  

    return render(request, 'fees/fee_payment.html', {'students': students})
@login_required
def make_payment(request):
    """Allow teachers, parents, or admins to make a payment for a student."""
    if request.user.is_staff:
        students = User.objects.filter(is_staff=False)  # Admin sees all students
    else:
        students = User.objects.filter(id=request.user.id)  # Teachers/parents see only themselves

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payer = request.user  # Automatically assign the payer
            payment.status = "Completed"  # Assume successful payment for now
            payment.save()
            return redirect('fees:payment_list')
    else:
        form = PaymentForm()

    return render(request, 'fees/make_payment.html', {'form': form, 'students': students})
