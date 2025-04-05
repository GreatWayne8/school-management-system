import requests
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Sum  
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.conf import settings
from datetime import date
from accounts.models import Parent
from .models import (
    AcademicYear, Student, FeeCategory,
    FeeStructure, FeeStatement, Payment
)
from django.db.models import Sum
from .mpesa_utils import (  
    calculate_balance,
    initiate_stk_push,
    get_mpesa_access_token,
    generate_mpesa_password,
    get_current_timestamp
)
from .forms import FeeStructureForm, PaymentForm, AcademicYearForm
from django.db.models import Count 
from .mpesa_utils import initiate_stk_push
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
User = get_user_model()

# Utility Functions
def is_admin(user):
    return user.is_staff

def get_current_academic_year():
    return AcademicYear.objects.filter(is_current=True).first()

# ---------------------------- #
# 1. ACADEMIC YEAR MANAGEMENT
# ---------------------------- #

@login_required
@user_passes_test(is_admin)
def manage_academic_years(request):
    years = AcademicYear.objects.all().order_by('-start_date')
    current_year = get_current_academic_year()
    
    if request.method == 'POST':
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            # Ensure only one current year exists
            if form.cleaned_data['is_current']:
                AcademicYear.objects.update(is_current=False)
            form.save()
            messages.success(request, 'Academic year saved successfully!')
            return redirect('fees:manage_academic_years')
    else:
        form = AcademicYearForm()

    return render(request, 'fees/academic_years.html', {
        'years': years,
        'current_year': current_year,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def set_current_year(request, year_id):
    AcademicYear.objects.update(is_current=False)
    year = get_object_or_404(AcademicYear, pk=year_id)
    year.is_current = True
    year.save()
    messages.success(request, f'{year.name} set as current academic year!')
    return redirect('fees:manage_academic_years')

# ---------------------------- #
# 2. FEE STRUCTURE MANAGEMENT
# ---------------------------- #

@login_required
@user_passes_test(is_admin)
def fee_structure_list(request):
    current_year = get_current_academic_year()
    structures = FeeStructure.objects.filter(
        academic_year=current_year
    ).select_related('category', 'academic_year')
    
    return render(request, 'fees/fee_structure_list.html', {
        'structures': structures,
        'current_year': current_year
    })

@login_required
@user_passes_test(is_admin)
def create_fee_structure(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure created successfully!')
            return redirect('fees:fee_structure_list')
    else:
        # Set current academic year as default
        initial = {'academic_year': get_current_academic_year()}
        form = FeeStructureForm(initial=initial)

    return render(request, 'fees/create_fee_structure.html', {
        'form': form,
        'title': 'Create New Fee Structure'
    })

@login_required
@user_passes_test(is_admin)
def edit_fee_structure(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure updated successfully!')
            return redirect('fees:fee_structure_list')
    else:
        form = FeeStructureForm(instance=structure)

    return render(request, 'fees/fee_structure_form.html', {
        'form': form,
        'title': 'Edit Fee Structure'
    })

@login_required
@user_passes_test(is_admin)
def toggle_fee_structure(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)
    structure.is_active = not structure.is_active
    structure.save()
    status = "activated" if structure.is_active else "deactivated"
    messages.success(request, f'Fee structure {status} successfully!')
    return redirect('fees:fee_structure_list')

# ---------------------------- #
# 3. PAYMENT MANAGEMENT
# ---------------------------- #

@login_required
def payment_list(request):
    today = date.today()
    query = request.GET.get('q', '')
    
    if request.user.is_staff:
        payments = Payment.objects.all()
    else:
        payments = Payment.objects.filter(
            Q(payer=request.user) | Q(student=request.user)
        ).distinct()
    
    if query:
        payments = payments.filter(
            Q(receipt_number__icontains=query) |
            Q(student__name__icontains=query) |
            Q(fee_structure__category__name__icontains=query)
        )
    
    # Calculate statistics
    total_paid = payments.filter(status='Completed').aggregate(
        Sum('amount_paid'))['amount_paid__sum'] or 0
    overdue = FeeStatement.objects.filter(
        is_overdue=True,
        balance__gt=0
    ).count()
    
    context = {
        'payments': payments,
        'today': today,
        'total_paid': total_paid,
        'overdue_count': overdue,
        'query': query
    }
    
    return render(request, 'fees/payment_list.html', context)

# fees/views.py
@login_required
def select_student_for_payment(request):
    # Get filter parameters
    level = request.GET.get('level')
    term = request.GET.get('term')
    academic_year_id = request.GET.get('academic_year')
    fee_category_id = request.GET.get('fee_category')
    
    # Base querysets
    students = Student.objects.all()
    fee_structures = FeeStructure.objects.filter(is_active=True)
    
    # Apply filters
    if level:
        students = students.filter(current_class__icontains=level)
    if term:
        fee_structures = fee_structures.filter(term=term)
    if academic_year_id:
        fee_structures = fee_structures.filter(academic_year_id=academic_year_id)
    if fee_category_id:
        fee_structures = fee_structures.filter(category_id=fee_category_id)
    
    academic_years = AcademicYear.objects.all()
    fee_categories = FeeCategory.objects.all()
    
    context = {
        'students': students,
        'fee_structures': fee_structures,
        'academic_years': academic_years,
        'fee_categories': fee_categories,
        'terms': FeeStructure.TERM_CHOICES,
        'selected_level': level,
        'selected_term': term,
        'selected_academic_year': academic_year_id,
        'selected_fee_category': fee_category_id,
    }
    return render(request, 'fees/select_student.html', context)

@login_required
def get_students(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse([], safe=False)
    
    students = Student.objects.filter(
        Q(name__icontains=query) |
        Q(admission_number__icontains=query)
    )[:10]  # Limit to 10 results
    
    results = [{
        'id': student.id,
        'text': f"{student.name} ({student.admission_number}) - {student.current_class}"
    } for student in students]
    
    return JsonResponse(results, safe=False)

@login_required
def make_payment(request, student_id=None):
    # Initialize
    initial = {}
    student = None
    fee_structure_id = request.GET.get('fee_structure')

    # PARENT LOGIC - Automatically get their child
    if request.user.is_parent:
        try:
            parent = Parent.objects.get(user=request.user)
            student = parent.student
            initial['student'] = student
        except Parent.DoesNotExist:
            messages.error(request, "No student linked to your account")
            return redirect('fees:payment_list')

    # ADMIN/TEACHER LOGIC - Allow selection if no student pre-selected
    elif student_id:
        student = get_object_or_404(Student, id=student_id)
        initial['student'] = student

    # Fee structure handling
    if fee_structure_id:
        fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)
        initial.update({
            'fee_structure': fee_structure,
            'amount_paid': fee_structure.amount
        })

    # Form handling
    if request.method == 'POST':
        form = PaymentForm(request.user, request.POST, initial=initial)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payer = request.user
            payment.save()
            messages.success(request, "Payment recorded successfully!")
            return redirect('fees:payment_receipt', pk=payment.id)
    else:
        form = PaymentForm(request.user, initial=initial)

    context = {
        'form': form,
        'student': student,  # Pass the specific student for parents
        'fee_structures': FeeStructure.objects.filter(is_active=True),
        'is_parent': request.user.is_parent,
        'CURRENCY_SYMBOL': 'Ksh'
    }

    # Only add student list for staff/teachers when no student pre-selected
    if not request.user.is_parent and not student_id:
        context['all_students'] = Student.objects.all().order_by('name')

    return render(request, 'fees/make_payment.html', context)


@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    # Security check - only admin, student or admin can view
    if not (request.user.is_staff or 
            request.user == payment.payer or 
            request.user == payment.student):
        messages.error(request, 'You are not authorized to view this receipt!')
        return redirect('fees:payment_list')
    
    return render(request, 'fees/receipt.html', {'payment': payment})

@login_required
def download_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    # Security check
    if not (request.user.is_staff or 
            request.user == payment.payer or 
            request.user == payment.student):
        return HttpResponse('Unauthorized', status=401)
    
    # Render HTML
    html_string = render_to_string('fees/receipt_pdf.html', {'payment': payment})
    html = HTML(string=html_string)
    
    # Create PDF
    result = html.write_pdf()
    
    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{payment.receipt_number}.pdf'
    response.write(result)
    
    return response

# ---------------------------- #
# 4. REPORTS & DASHBOARD
# ---------------------------- #

@login_required
@user_passes_test(is_admin)
def fee_dashboard(request):
    current_year = get_current_academic_year()
    
    # Fee collection summary
    payments = Payment.objects.filter(
        fee_structure__academic_year=current_year
    )
    total_collected = payments.filter(status='Completed').aggregate(
        Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Overdue fees
    overdue = FeeStatement.objects.filter(
        fee_structure__academic_year=current_year,
        is_overdue=True,
        balance__gt=0
    ).select_related('student', 'fee_structure')
    
    # Payment methods breakdown
    payment_methods = payments.values('payment_method').annotate(
        total=Sum('amount_paid'),
        count=Count('id')  # Changed from models.Count to just Count
    )
    
    context = {
        'current_year': current_year,
        'total_collected': total_collected,
        'overdue_fees': overdue,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'fees/dashboard.html', context)
@login_required
def student_statement(request, student_id=None):
    if student_id and request.user.is_staff:
        student = get_object_or_404(Student, pk=student_id)
    else:
        student = request.user
    
    statements = FeeStatement.objects.filter(
        student=student
    ).select_related('fee_structure', 'fee_structure__category')
    
    total_balance = statements.aggregate(
        Sum('balance'))['balance__sum'] or 0
    
    return render(request, 'fees/student_statement.html', {
        'statements': statements,
        'student': student,
        'total_balance': total_balance
    })

@login_required
@user_passes_test(is_admin)
def delete_fee_structure(request, pk):
    fee = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee structure deleted successfully!')
        return redirect('fees:fee_structure_list')
    return render(request, 'fees/confirm_delete.html', {'fee': fee})


# -------------------------------------------------------------------------------------------------------------------------------------------
#                                         Daraja Mpesa
# -------------------------------------------------------------------------------------------------------------------------------------------

def update_fee_statement(payment):
    """
    Update the student's fee statement after a successful payment
    """
    try:
        statement, created = FeeStatement.objects.get_or_create(
            student=payment.student,
            fee_structure=payment.fee_structure,
            defaults={
                'total_amount': payment.fee_structure.amount,
                'amount_paid': payment.amount_paid,
                'balance': payment.fee_structure.amount - payment.amount_paid,
                'last_payment_date': payment.payment_date
            }
        )
        
        if not created:
            statement.amount_paid += payment.amount_paid
            statement.balance = statement.total_amount - statement.amount_paid
            statement.last_payment_date = payment.payment_date
            statement.save()
            
            # Check if fee is fully paid
            if statement.balance <= 0:
                statement.fully_paid = True
                statement.payment_completion_date = timezone.now()
                statement.save()
        
        return True
    except Exception as e:
        print(f"Error updating fee statement: {str(e)}")
        return False

def send_payment_receipt(payment):
    """
    Send payment receipt email using the dedicated payment_receipt_email.html template
    """
    try:
        context = {
            'payment': payment,
            'student': payment.student,
            'school_name': "Vihiga Education City",  
            'contact_email': "finance@vihigaeducationcity.sc.ke",
            'contact_phone': "+254701728763",
        }

        html_content = render_to_string('fees/payment_receipt_email.html', context)
        
        text_content = strip_tags(html_content)

        # Prepare email
        subject = f"Payment Receipt - {payment.receipt_number}"
        from_email = "Vihiga Education City School <noreply@vihigaeducationcity.sc.ke>"
        
        # Determine recipient(s)
        recipients = [payment.payer.email]
        if hasattr(payment.student, 'parent') and payment.student.parent.email:
            recipients.append(payment.student.parent.email)

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipients,
            reply_to=[context['contact_email']]
        )
        msg.attach_alternative(html_content, "text/html")

        # Optional: Attach PDF receipt
        # pdf_content = generate_pdf_receipt(payment) 
        # msg.attach(f'receipt_{payment.receipt_number}.pdf', pdf_content, 'application/pdf')

        # Send email
        msg.send(fail_silently=False)
        
        # Log successful sending
        payment.email_sent = True
        payment.email_sent_at = timezone.now()
        payment.save()
        
        return True
    except Exception as e:
        # Log the error
        print(f"Error sending payment receipt email: {str(e)}")
        
        # Update payment record with failure
        payment.email_sent = False
        payment.email_attempts = (payment.email_attempts or 0) + 1
        payment.save()
        
        return False

def initiate_mpesa_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Calculate balance for initial form data
    balance_info = calculate_balance(student)
    initial_amount = balance_info['balance'] if balance_info['balance'] > 0 else 0
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payer = request.user
            payment.student = student
            
            # Validate payment amount doesn't exceed balance
            if payment.amount_paid > balance_info['balance']:
                messages.error(request, 'Payment amount cannot exceed outstanding balance')
                return render(request, 'fees/make_payment.html', {
                    'form': form,
                    'student': student,
                    'default_phone': settings.MPESA_TEST_PHONE
                })
            
            # For M-Pesa payments
            if payment.payment_method == 'MPesa':
                phone_number = request.POST.get('phone_number', settings.MPESA_TEST_PHONE)
                
                try:
                    # Format phone number (convert 07... to 2547...)
                    formatted_phone = f"254{phone_number[1:]}" if phone_number.startswith('0') else phone_number
                    
                    response = initiate_stk_push(
                        phone_number=formatted_phone,
                        amount=payment.amount_paid,
                        account_reference=payment.receipt_number
                    )
                    
                    if response.get('ResponseCode') == '0':
                        payment.status = 'Pending'
                        payment.transaction_reference = response.get('CheckoutRequestID')
                        payment.phone_number = formatted_phone  # Store formatted number
                        payment.save()
                        
                        messages.success(request, 'Payment initiated! Check your phone to complete M-Pesa payment.')
                        return redirect('fees:payment_list')
                    else:
                        error_message = response.get('errorMessage', 'Failed to initiate payment')
                        messages.error(request, f'M-Pesa Error: {error_message}')
                        
                except Exception as e:
                    messages.error(request, f'Error processing payment: {str(e)}')
            else:
                # For non-M-Pesa payments
                payment.status = 'Completed'
                payment.save()
                
                # Update fee statement immediately for non-M-Pesa payments
                update_fee_statement(payment)
                send_payment_receipt(payment)
                
                messages.success(request, 'Payment recorded successfully!')
                return redirect('fees:payment_receipt', pk=payment.id)
    else:
        form = PaymentForm(initial={
            'amount_paid': initial_amount,
            'payment_method': 'MPesa'  # Default to M-Pesa
        })
    
    return render(request, 'fees/make_payment.html', {
        'form': form,
        'student': student,
        'default_phone': settings.MPESA_TEST_PHONE,
        'balance_info': balance_info  # Pass to template 
    })

def initiate_stk_push(phone_number, amount, account_reference):
    """Initiate M-Pesa STK push"""
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": generate_mpesa_password(),
        "Timestamp": get_current_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(int(amount)),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "School Fees Payment"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            if result_code == '0':
                # Successful payment
                payment = Payment.objects.get(transaction_reference=checkout_request_id)
                payment.status = 'Completed'
                
                # Get M-Pesa transaction details
                callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_code = item.get('Value')
                    elif item.get('Name') == 'PhoneNumber':
                        payment.phone_number = item.get('Value')
                
                payment.save()
                
                # Update fee statement
                update_fee_statement(payment)
                
                # Send receipt to payer
                send_payment_receipt(payment)
                
                return JsonResponse({'status': 'success'})
            else:
                # Failed payment
                error_message = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc', 'Payment failed')
                payment = Payment.objects.get(transaction_reference=checkout_request_id)
                payment.status = 'Failed'
                payment.notes = error_message
                payment.save()
                
                return JsonResponse({'status': 'failed', 'error': error_message})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=400)

def test_mpesa_integration(request):
    """Test endpoint for M-Pesa integration"""
    test_phone = "254701728763"  # Your test phone number
    test_amount = 1  # Test with 1 KES
    test_reference = "TEST123"
    
    try:
        # 1. Test authentication
        token = get_mpesa_access_token()
        if not token:
            return JsonResponse({"status": "error", "message": "Authentication failed"}, status=500)
        
        # 2. Test STK push
        response = initiate_stk_push(test_phone, test_amount, test_reference)
        
        if response.get('ResponseCode') == '0':
            return JsonResponse({
                "status": "success",
                "message": "STK push initiated successfully",
                "data": {
                    "CheckoutRequestID": response.get('CheckoutRequestID'),
                    "MerchantRequestID": response.get('MerchantRequestID')
                }
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": response.get('errorMessage', 'Unknown error'),
                "response": response
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

    
def test_auth(request):
    from requests.auth import HTTPBasicAuth
    import requests
    
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    
    try:
        response = requests.get(url, auth=auth)
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)