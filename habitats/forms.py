from django import forms
from .models import Habitat

class HabitatForm(forms.ModelForm):
    class Meta:
        model = Habitat
        fields = ['name', 'area', 'max_capacity', 'environment_status']
        labels = {
            'name': 'Nama Habitat',
            'area': 'Luas Area',
            'max_capacity': 'Kapasitas Maksimal',
            'environment_status': 'Status Lingkungan',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '[isian]'}),
            'area': forms.TextInput(attrs={'placeholder': '[isian] (dalam m²)'}),
            'max_capacity': forms.TextInput(attrs={'placeholder': '[isian] (jumlah hewan)'}),
            'environment_status': forms.Textarea(attrs={
                'placeholder': '[tekstarea] (contoh: Suhu: 28°C, Kelembapan: 70%, Vegetasi lebat)',
                'rows': 3
            }),
        }