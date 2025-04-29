from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FeedingSchedule
from .forms import FeedingScheduleForm

@login_required
def feeding_list(request):
    feedings = FeedingSchedule.objects.filter(penjaga=request.user).order_by('jadwal')
    return render(request, 'feeding/feeding_list.html', {'feedings': feedings})

@login_required
def add_feeding(request):
    if request.method == 'POST':
        form = FeedingScheduleForm(request.POST)
        if form.is_valid():
            feeding = form.save(commit=False)
            feeding.penjaga = request.user
            feeding.save()
            return redirect('feeding_list')
    else:
        form = FeedingScheduleForm()
    return render(request, 'feeding/add_feeding.html', {'form': form})

@login_required
def edit_feeding(request, feeding_id):
    feeding = get_object_or_404(FeedingSchedule, id=feeding_id, penjaga=request.user)
    if request.method == 'POST':
        form = FeedingScheduleForm(request.POST, instance=feeding)
        if form.is_valid():
            form.save()
            return redirect('feeding_list')
    else:
        form = FeedingScheduleForm(instance=feeding)
    return render(request, 'feeding/edit_feeding.html', {'form': form})

@login_required
def delete_feeding(request, feeding_id):
    feeding = get_object_or_404(FeedingSchedule, id=feeding_id, penjaga=request.user)
    if request.method == 'POST':
        feeding.delete()
        return redirect('feeding_list')
    return render(request, 'feeding/delete_feeding.html', {'feeding': feeding})

@login_required
def mark_as_done(request, feeding_id):
    feeding = get_object_or_404(FeedingSchedule, id=feeding_id, penjaga=request.user)
    feeding.status = 'Selesai Diberikan'
    feeding.save()
    return redirect('feeding_list')
