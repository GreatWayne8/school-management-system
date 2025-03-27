import os
import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.conf import settings
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
from .models import FeeStructure, Payment, FeeCategory, FeeStatement
from .forms import PaymentForm, FeeStructureForm
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import FeeStatementSerializer

User = get_user_model()

# Check if user is admin
def is_admin(user):
    return user.is_staff

# ---------------------------- #
# 1. FEE STRUCTURE MANAGEMENT
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
def fee_structure_list(request):
    """List all fee structures (visible to all users)."""
    fee_structures = FeeStructure.objects.all()
    return render(request, 'fees/fee_structure_list.html', {'fee_structures': fee_structures})

@login_required
def fee_structure_view(request):
    """Admin can edit fee structures, students can only view them."""
    fee_structures = FeeStructure.objects.all()

    if request.user.is_staff:  
        if request.method == 'POST':
            form = FeeStructureForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('fees:fee_structure')
        else:
            form = FeeStructureForm()
    else:
        form = None  

    return render(request, 'fees/fee_structure.html', {'fee_structures': fee_structures, 'form': form})

# ---------------------------- #
# 2. FEE PAYMENT MANAGEMENT
# ---------------------------- #

@login_required
def payment_list(request):
    """Admin sees all payments, students see only their payments."""
    if request.user.is_staff:
        payments = Payment.objects.all()
    else:
        payments = Payment.objects.filter(student=request.user)

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
        students = User.objects.filter(is_staff=False)  # List of students (non-admin users)
    else:
        students = None  # Regular users cannot select other students

    return render(request, 'fees/fee_payment.html', {'students': students})

# ---------------------------- #
# 3. FEE STATEMENTS (API)
# ---------------------------- #

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def fee_statement_list_create(request):
    """Admin can create fee statements, users can view them."""
    if request.method == 'GET':
        if request.user.is_staff:
            statements = FeeStatement.objects.all()
        else:
            statements = FeeStatement.objects.filter(student=request.user)

        serializer = FeeStatementSerializer(statements, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=403)

        serializer = FeeStatementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def fee_statement_detail(request, pk):
    """Admin can update/delete fee statements, users can only view theirs."""
    statement = get_object_or_404(FeeStatement, id=pk)

    if not request.user.is_staff and statement.student != request.user:
        return Response({"error": "Permission denied"}, status=403)

    if request.method == 'GET':
        serializer = FeeStatementSerializer(statement)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=403)

        serializer = FeeStatementSerializer(statement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=403)

        statement.delete()
        return Response({"message": "Fee statement deleted successfully"}, status=204)
