from django import forms
from .models import Atraksi, Wahana
from animals.models import Animal
from django.contrib.auth.models import User

from django import forms

class AtraksiForm(forms.Form):
    nama_atraksi = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Nama atraksi'
        })
    )

    lokasi = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Lokasi atraksi'
        })
    )

    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Kapasitas maksimum'
        })
    )

    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]'
        })
    )

    pelatih = forms.MultipleChoiceField(
        choices=[('budi', 'Budi'), ('andi', 'Andi'), ('havana', 'Havana')],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2 ml-1'
        })
    )

    hewan = forms.MultipleChoiceField(
        choices=[('hewan_1', 'Zebra'), ('hewan_2', 'Macan'), ('hewan_3', 'Panda')],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2 ml-1'
        })
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
    nama_wahana = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Nama Wahana',
        })
    )
    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Kapasitas Maksimal',
        })
    )
    jadwal = forms.TimeField(
        label='Jadwal Wahana',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
        })
    )
    peraturan = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'rows': 4,
            'placeholder': 'Peraturan',
        }),
        required=True
    )

class EditWahanaForm(forms.Form):
    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Kapasitas Maksimal',
        })
    )
    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
        })
    )
