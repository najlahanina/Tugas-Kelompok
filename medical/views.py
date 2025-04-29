from django.shortcuts import render, redirect, get_object_or_404
from .models import MedicalRecord
from .forms import MedicalRecordForm, EditMedicalRecordForm
from .models import HealthCheckSchedule
from .forms import HealthCheckScheduleForm

def record_list(request):
    records = MedicalRecord.objects.all()
    return render(request, 'medical_records/record_list.html', {'records': records})

def add_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('record_list')
    else:
        form = MedicalRecordForm()
    return render(request, 'medical_records/add_record.html', {'form': form})

def edit_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.method == 'POST':
        form = EditMedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('record_list')
    else:
        form = EditMedicalRecordForm(instance=record)
    return render(request, 'medical_records/edit_record.html', {'form': form})

def delete_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
        return redirect('record_list')
    return render(request, 'medical_records/delete_record.html', {'record': record})

def health_check_schedule(request):
    schedules = HealthCheckSchedule.objects.all().order_by('tanggal_pemeriksaan_selanjutnya')

    if request.method == 'POST':
        form = HealthCheckScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('health_check_schedule')
    else:
        form = HealthCheckScheduleForm()

    return render(request, 'medical_records/health_check_schedule.html', {'schedules': schedules, 'form': form})