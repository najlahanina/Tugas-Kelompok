from django import forms
from .models import MedicalRecord
from .models import HealthCheckSchedule

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['tanggal_pemeriksaan', 'nama_dokter', 'status_kesehatan', 'diagnosis', 'pengobatan']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status_kesehatan')
        diagnosis = cleaned_data.get('diagnosis')
        pengobatan = cleaned_data.get('pengobatan')

        if status == 'Sakit':
            if not diagnosis:
                self.add_error('diagnosis', 'Diagnosis wajib diisi untuk status Sakit.')
            if not pengobatan:
                self.add_error('pengobatan', 'Pengobatan wajib diisi untuk status Sakit.')

class EditMedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['catatan_tindak_lanjut', 'diagnosis', 'pengobatan']

class HealthCheckScheduleForm(forms.ModelForm):
    class Meta:
        model = HealthCheckSchedule
        fields = ['tanggal_pemeriksaan_selanjutnya']
        widgets = {
            'tanggal_pemeriksaan_selanjutnya': forms.DateInput(attrs={'type': 'date'})
        }
