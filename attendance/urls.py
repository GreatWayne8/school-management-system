# from django.urls import path
# from . import views

# app_name = 'attendance'

# urlpatterns = [
#     path('clock-in/', views.clock_in, name='clock_in'),
#     path('clock-out/', views.clock_out, name='clock_out'),
#     path('clock-status/', views.clock_status, name='clock_status'),
#     path('teacher/check-in-student/<int:student_id>/', views.teacher_check_in_student, name='teacher_check_in_student'),
#     path('teacher/check-out-student/<int:student_id>/', views.teacher_check_out_student, name='teacher_check_out_student'),
#     path('records/', views.ClockInOutRecordsView.as_view(), name='clock_in_out_records'),
#     path('teacher-records/', views.TeacherClockInOutRecordsView.as_view(), name='teacher_records'),
#     path('student-records/', views.StudentClockInOutRecordsView.as_view(), name='student_records'),
# ]
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('clock-status/', views.clock_status, name='clock_status'),
    path('view-history/', views.view_history, name='view_history'),
    path('teacher/check-in-student/<int:student_id>/', views.teacher_check_in_student, name='teacher_check_in_student'),
    
    # path('teacher/check-out-student/<int:student_id>/', views.teacher_check_out_student, name='teacher_check_out_student'),
    path('records/', views.ClockInOutRecordsView.as_view(), name='clock_in_out_records'),
    path('teacher-records/', views.TeacherClockInOutRecordsView.as_view(), name='teacher_records'),
    path('student-records/', views.StudentClockInOutRecordsView.as_view(), name='student_records'),
    path('student-check-in-list/', views.StudentClockInOutRecordsView.as_view(), name='student_check_in_list'),

]
