from django.shortcuts import render, redirect
from .models import FeeStructure, Payment
from .forms import PaymentForm


def fee_payment_view(request):
    fee_structures = FeeStructure.objects.all()

    payments = Payment.objects.filter(student=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user  
            payment.save()
            return redirect('fees:fee_payment')  
    else:
        form = PaymentForm()

    context = {
        'fee_structures': fee_structures,
        'payments': payments,
        'form': form,
    }

    return render(request, 'fees/fee_payment.html', context)
