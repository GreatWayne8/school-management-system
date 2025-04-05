from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    # Fee Structure Management
    path('fee-structure/', views.fee_structure_list, name='fee_structure_list'),
    path('fee-structure/create/', views.create_fee_structure, name='create_fee_structure'),
    path('fee-structure/edit/<int:pk>/', views.edit_fee_structure, name='edit_fee_structure'),
    path('fee-structure/delete/<int:pk>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('fee-structure/toggle/<int:pk>/', views.toggle_fee_structure, name='toggle_fee_structure'),
    path('select-student/', views.select_student_for_payment, name='select_student'),
    path('make-payment/<int:student_id>/', views.make_payment, name='make_payment'), 
    path('get-students/', views.get_students, name='get_students'),
    # Payment Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/make/', views.make_payment, name='make_payment'),
    path('payments/receipt/<int:pk>/', views.payment_receipt, name='payment_receipt'),
    path('payments/download/<int:pk>/', views.download_receipt, name='download_receipt'),
    
    # Academic Year Management
    path('academic-years/', views.manage_academic_years, name='manage_academic_years'),
    path('academic-years/set-current/<int:year_id>/', views.set_current_year, name='set_current_year'),
    
    # Reports
    path('dashboard/', views.fee_dashboard, name='dashboard'),
    path('statements/', views.student_statement, name='student_statement'),  
    path('statements/<int:student_id>/', views.student_statement, name='student_statement'), 

    path('test-mpesa/', views.test_mpesa_integration, name='test_mpesa'),
    path('test-auth/', views.test_auth, name='test_auth')

]