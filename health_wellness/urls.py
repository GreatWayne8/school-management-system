from django.urls import path
from . import views

urlpatterns = [
    path('medical_records/', views.medical_record_list, name='medical_record_list'),
    
    path('medical_records/create/<int:student_id>/', views.medical_record_create, name='medical_record_create'),
    
    path('medical_records/<int:record_id>/edit/', views.medical_record_update, name='medical_record_update'),
    
    path('medical_records/<int:student_id>/', views.medical_record_detail, name='medical_record_detail'),
    
    path('wellness_programs/', views.wellness_program_list, name='wellness_program_list'),
]
