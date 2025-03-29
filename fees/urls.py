from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    # Fee Structure URLs
    path('fee-structure/create/', views.create_fee_structure, name='create_fee_structure'),
    path('fee-structure/edit/<int:fee_id>/', views.edit_fee_structure, name='edit_fee_structure'),
    path('fee-structure/delete/<int:fee_id>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('fee-structure/', views.fee_structure_list, name='fee_structure_list'),

    # Payment URLs
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/pay/', views.fee_payment_view, name='make_payment'),  # Make a payment
    path('payments/receipt/<int:payment_id>/', views.generate_receipt, name='generate_receipt'),
]
