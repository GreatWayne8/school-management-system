from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import ClockInOut
from django.views.generic import ListView
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def clock_in(request):
    today = timezone.now().date()
    clock_in_record, created = ClockInOut.objects.get_or_create(user=request.user, date=today)
    
    if request.method == "POST":
        if clock_in_record.clock_in_time:
            messages.error(request, "You have already clocked in today.")
        else:
            clock_in_record.clock_in_time = timezone.now()
            clock_in_record.save()
            messages.success(request, "You have successfully clocked in.")
        
        return redirect('attendance:clock_status')
    
    return render(request, 'attendance/clock_in.html', {'clock_in_record': clock_in_record})

@login_required
def clock_out(request):
    today = timezone.now().date()
    clock_in_record = ClockInOut.objects.filter(user=request.user, date=today, clock_out_time__isnull=True).first()

    if not clock_in_record or not clock_in_record.clock_in_time:
        messages.error(request, "You haven't clocked in yet today, so you can't clock out.")
        return redirect('attendance:clock_status')

    if request.method == "POST":
        clock_in_record.clock_out_time = timezone.now()
        clock_in_record.save()
        messages.success(request, "You have successfully clocked out.")
        return redirect('attendance:clock_status')

    return render(request, 'attendance/clock_out.html', {'clock_in_record': clock_in_record})



@login_required
def view_history(request):
    today = timezone.now().date()
    clock_in_records = ClockInOut.objects.filter(user=request.user, date=today)
    
    return render(request, 'attendance/view_history.html', {'clock_in_records': clock_in_records})

@login_required
def clock_status(request):
    today = timezone.now().date()
    clock_record = ClockInOut.objects.filter(user=request.user, date=today).first()
    students = User.objects.filter(is_student=True)

    context = {
        'clock_record': clock_record,
        'today': today,
        'students': students  # Add students to context
    }

    return render(request, 'attendance/clock_status.html', context)

@login_required
def student_check_in_list(request):
    today = timezone.now().date()

    # Fetch students from the database with is_student=True
    students = User.objects.filter(is_student=True)
    if not students.exists():
        print("No students found!")

    for student in students:
        student.clockedin = ClockInOut.objects.filter(user=student, date=today, clock_out_time__isnull=True).exists()

    return render(request, 'attendance/student_check_in_list.html', {
        'students': students,
        'today': today,
    })


class ClockInOutRecordsView(ListView):
    model = ClockInOut
    template_name = 'attendance/clock_in_out_records.html'
    context_object_name = 'records'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ClockInOut.objects.all()  # Admin view all records
        return ClockInOut.objects.none()

class TeacherClockInOutRecordsView(ListView):
    model = ClockInOut
    template_name = 'attendance/teacher_records.html'
    context_object_name = 'records'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ClockInOut.objects.filter(user__is_teacher=True)
        return ClockInOut.objects.none()

class StudentClockInOutRecordsView(ListView):
    model = ClockInOut
    template_name = 'attendance/student_records.html'
    context_object_name = 'records'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ClockInOut.objects.filter(user__is_student=True)
        return ClockInOut.objects.none()
    

@login_required
def teacher_check_in_student(request, student_id):
    student = get_object_or_404(User, id=student_id, is_student=True)
    today = timezone.now().date()

    print(f"Student fetched: {student.username} (ID: {student.id})")

    existing_check_in = ClockInOut.objects.filter(user=student, date=today, clock_out_time__isnull=True).exists()

    print(f"Existing check-in status: {existing_check_in}")

    if existing_check_in:
        messages.error(request, f"{student.username} is already checked in for today.")
        return redirect('attendance:clock_status')

    if request.method == "POST":
        print("Form submitted!")

        ClockInOut.objects.create(
            user=student,
            date=today,
            clock_in_time=timezone.now()
        )
        messages.success(request, f"{student.username} has been successfully checked in.")
        return redirect('attendance:clock_status')

    return render(request, 'attendance/teacher_check_in_student.html', {'student': student})


@login_required
def student_list(request):
    students = User.objects.filter(is_student=True)
    return render(request, 'attendance/student_list.html', {'students': students})

@login_required
def student_records(request):
    today = timezone.now().date()
    checked_in_students = ClockInOut.objects.filter(
        user__is_student=True,  
        date=today,
        clock_out_time__isnull=True 
    ).distinct('user')   

    return render(request, 'attendance/student_records.html', {
        'today': today,
        'checked_in_students': checked_in_students
    })


# @login_required
# def teacher_check_in_student(request, student_id):
#     student = get_object_or_404(User, id=student_id, is_student=True)
#     today = timezone.now().date()

#     existing_check_in = ClockInOut.objects.filter(
#         user=student,
#         date=today
#     ).exists()

#     if existing_check_in:
#         messages.error(request, "The student is already checked in for today.")
#         return redirect('attendance:clock_status')

#     if request.method == "POST":
#         ClockInOut.objects.create(
#             user=student,
#             date=today,
#             clock_in_time=timezone.now()
#         )
#         messages.success(request, f"{student.username} has been successfully checked in.")
#         return redirect('attendance:clock_status')

#     return render(request, 'attendance/teacher_check_in_student.html', {'student': student})

@login_required
def teacher_check_out_student(request, student_id):
    student = get_object_or_404(User, id=student_id, is_student=True)
    
    # Get the clock in record for today
    clock_in_record = ClockInOut.objects.filter(user=student, date=timezone.now().date(), clock_out_time__isnull=True).first()
    
    if not clock_in_record:
        messages.error(request, "The student is not checked in today, so cannot be checked out.")
        return redirect('attendance:clock_status')
    
    if request.method == "POST":
        # Do nothing to the clock_out_time, preventing the student from being checked out.
        messages.success(request, f"{student.username} is already checked in and will remain checked in for the day.")
        return redirect('attendance:clock_status')

    return render(request, 'attendance/teacher_check_out_student.html', {'student': student})