from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('view-history/', views.view_history, name='view_history'),
    path('clock-status/', views.clock_status, name='clock_status'),
    path('student-check-in-list/', views.student_check_in_list, name='student_check_in_list'),
    path('teacher-check-in-student/<int:student_id>/', views.teacher_check_in_student, name='teacher_check_in_student'),
    path('student-list/', views.student_list, name='student_list'),
    # path('student-records/', views.student_records, name='student_records'),
    path('teacher-check-out-student/<int:student_id>/', views.teacher_check_out_student, name='teacher_check_out_student'),
    path('clock-in-out-records/', views.ClockInOutRecordsView.as_view(), name='clock_in_out_records'),
    path('teacher-records/', views.TeacherClockInOutRecordsView.as_view(), name='teacher_records'),
    path('student-records/', views.StudentClockInOutRecordsView.as_view(), name='student_records'),
]
