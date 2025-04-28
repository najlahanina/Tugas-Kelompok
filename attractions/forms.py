from django import forms
from .models import Atraksi, Wahana
from animals.models import Animal
from django.contrib.auth.models import User

class AtraksiForm(forms.Form):
    nama_atraksi = forms.CharField(max_length=50)
    lokasi = forms.CharField(max_length=100)
    kapasitas_max = forms.IntegerField()
    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    pelatih = forms.ChoiceField(choices=[('budi', 'Budi'), ('andi', 'Andi'), ('havana', 'Havana')])  # dummy
    hewan = forms.MultipleChoiceField(
        choices=[('hewan_1', 'Hewan 1'), ('hewan_2', 'Hewan 2'), ('hewan_3', 'Hewan 3')],
        widget=forms.CheckboxSelectMultiple
    )

class EditAtraksiForm(forms.Form):
    kapasitas_max = forms.IntegerField(
        label='Kapasitas Maksimum',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )


class WahanaForm(forms.Form):
    nama_wahana = forms.CharField(max_length=50)
    kapasitas_max = forms.IntegerField()
    jadwal = forms.TimeField(
        label='Jadwal Wahana',
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    peraturan = forms.CharField(widget=forms.Textarea, required=True)

class EditWahanaForm(forms.Form):
    nama_wahana = forms.CharField(max_length=50)
    kapasitas_max = forms.IntegerField()
    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
