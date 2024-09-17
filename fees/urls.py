from django.urls import path
from .views import fee_payment_view

app_name = 'fees'

urlpatterns = [
       path('fee-payment/', fee_payment_view, name='fee_payment'),

]
