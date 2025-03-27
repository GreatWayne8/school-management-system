from django.urls import path
from .views import fee_payment_view, create_fee_structure

app_name = 'fees'

urlpatterns = [
    path('fee-payment/', fee_payment_view, name='fee_payment'),
    path('create-fee/', create_fee_structure, name='create_fee_structure'), 
    path('fee-statements/', FeeStatementListCreateView, name='fee-statement-list-create'),
    path('fee-statements/<int:pk>/', FeeStatementRetrieveUpdateDeleteView.as_view(), name='fee-statement'), 
    # path("mpesa_callback/", mpesa_callback, name="mpesa_callback"),
    # path('mpesa/token/', get_mpesa_token, name='mpesa_token'),


]
