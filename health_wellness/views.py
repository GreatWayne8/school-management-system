from django.shortcuts import render, get_object_or_404, redirect
from .models import MedicalRecord,WellnessProgram
from .forms import MedicalRecordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.models import Student

User=get_user_model()

def add_medical_record(request, student_id):
    student = Student.objects.get(id=student_id)  
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.student = student  
            medical_record.save()
            return redirect('medical_record_list')
    else:
        form = MedicalRecordForm()
    return render(request, 'add_medical_record.html', {'form': form, 'student': student})


def medical_record_list(request):
    records = MedicalRecord.objects.all()
    return render(request, 'health_wellness/medical_record_list.html', {'records': records})

# def medical_record_create(request, student_id):
#     student = get_object_or_404(Student, id=student_id)
#     if request.method == 'POST':
#         form = MedicalRecordForm(request.POST)
#         if form.is_valid():
#             record = form.save(commit=False)
#             record.student = student
#             record.save()
#             return redirect('medical_record_list')
#     else:
#         form = MedicalRecordForm()
#     return render(request, 'health_wellness/medical_record_form.html', {'form': form, 'student': student})

def medical_record_create(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.student  # Access the User instance through the 'student' field

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.student = user 
            medical_record.save()
            return redirect('medical_record_list')  
    else:
        form = MedicalRecordForm()

    return render(request, 'health_wellness/medical_record_form.html', {'form': form})


def medical_record_update(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    # Handle the update logic
    return render(request, 'health_wellness/medical_record_form.html', {'record': record})

def medical_record_detail(request, student_id):
    # Get the student instance using student_id
    student = get_object_or_404(User, id=student_id)  # Assuming 'User' is your model

    # Query MedicalRecord using the student instance
    records = MedicalRecord.objects.filter(student=student)

    context = {
        'student': student,
        'records': records,
    }

    return render(request, 'health_wellness/medical_record_detail.html', context)

def wellness_program_list(request):
    programs = WellnessProgram.objects.all()
    return render(request, 'health_wellness/wellness_program_list.html', {'programs': programs})
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'health_wellness/student_detail.html', {'student': student})
