from django import forms
from .models import FeedingSchedule

class FeedingScheduleForm(forms.ModelForm):
    class Meta:
        model = FeedingSchedule
        fields = ['jenis_pakan', 'jumlah_pakan', 'jadwal']
        widgets = {
            'jadwal': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
