from django import forms
from django.contrib.auth.models import User
from attractions.models import Atraksi
from .models import Reservasi
from django.utils import timezone

class ReservasiForm(forms.Form):
    ATRAKSI_CHOICES = [
        ('Pertunjukan lumba-lumba', 'Pertunjukan lumba-lumba'),
        ('Feeding time harimau', 'Feeding time harimau'),
        ('Bird show', 'Bird show'),
    ]
    
    nama_atraksi = forms.ChoiceField(choices=ATRAKSI_CHOICES)
    tanggal_kunjungan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    jumlah_tiket = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super(ReservasiForm, self).__init__(*args, **kwargs)
        self.fields['tanggal_kunjungan'].widget.attrs['min'] = timezone.now().date().isoformat()

class ReservasiEditForm(forms.ModelForm):
    class Meta:
        model = Reservasi
        fields = ['jumlah_tiket', 'status']

    def __init__(self, *args, **kwargs):
        super(ReservasiEditForm, self).__init__(*args, **kwargs)
        
        # For admin users, allow status change
        if kwargs.get('instance'):
            reservasi = kwargs['instance']
            self.fields['nama_atraksi'] = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                                         initial=reservasi.nama_atraksi,
                                                         required=False)
            self.fields['tanggal_kunjungan'] = forms.DateField(widget=forms.DateInput(attrs={'readonly': 'readonly'}),
                                                             initial=reservasi.tanggal_kunjungan,
                                                             required=False)

class AdminReservasiEditForm(forms.ModelForm):
    class Meta:
        model = Reservasi
        fields = ['jumlah_tiket', 'status']
        
    def __init__(self, *args, **kwargs):
        super(AdminReservasiEditForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            reservasi = kwargs['instance']
            self.fields['username_p'] = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                                       initial=reservasi.username_p.username,
                                                       required=False)
            self.fields['nama_atraksi'] = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                                         initial=reservasi.nama_atraksi,
                                                         required=False)
            self.fields['tanggal_kunjungan'] = forms.DateField(widget=forms.DateInput(attrs={'readonly': 'readonly'}),
                                                             initial=reservasi.tanggal_kunjungan,
                                                             required=False)