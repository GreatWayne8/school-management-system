import base64
import datetime
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.db.models import Sum
from .models import FeeStatement, Payment

def get_mpesa_access_token():
    """Get M-Pesa OAuth access token"""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

def generate_mpesa_password():
    """Generate M-Pesa API password"""
    timestamp = get_current_timestamp()
    data = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(data.encode()).decode()

def get_current_timestamp():
    """Get current timestamp in YYYYMMDDHHMMSS format"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

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
        "PartyA": f"254{phone_number[1:]}",  
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": f"254{phone_number[1:]}",
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "School Fees Payment"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def calculate_balance(student):
    """
    Calculate the current fee balance for a student
    Returns: Tuple of (total_due, total_paid, balance)
    """
    # Get all fee statements for the student
    fee_statements = FeeStatement.objects.filter(student=student)
    
    # Calculate total amounts
    total_due = fee_statements.aggregate(total=Sum('fee_structure__amount'))['total'] or 0
    total_paid = fee_statements.aggregate(total=Sum('amount_paid'))['total'] or 0
    balance = total_due - total_paid
    
    return {
        'total_due': total_due,
        'total_paid': total_paid,
        'balance': balance
    }