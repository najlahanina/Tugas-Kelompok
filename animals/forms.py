from django import forms
from .models import Animal
from habitats.models import Habitat

class AnimalForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Tanggal Lahir"
    )
    
    habitat = forms.ModelChoiceField(
        queryset=Habitat.objects.all(),
        label="Nama Habitat",
        empty_label="Pilih habitat"
    )
    
    class Meta:
        model = Animal
        fields = ['name', 'species', 'origin', 'birth_date', 'health_status', 'habitat', 'photo_url']
        labels = {
            'name': 'Nama Individu',
            'species': 'Spesies',
            'origin': 'Asal Hewan',
            'health_status': 'Status Kesehatan',
            'photo_url': 'URL Foto Satwa',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '[isian] (opsional)'}),
            'species': forms.TextInput(attrs={'placeholder': '[isian]'}),
            'origin': forms.TextInput(attrs={'placeholder': '[isian]'}),
            'photo_url': forms.URLInput(attrs={'placeholder': '[isian]'}),
        }