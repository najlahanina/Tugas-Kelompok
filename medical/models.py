from django.db import models

class MedicalRecord(models.Model):
    STATUS_CHOICES = [
        ('Sehat', 'Sehat'),
        ('Sakit', 'Sakit'),
    ]

    tanggal_pemeriksaan = models.DateField()
    nama_dokter = models.CharField(max_length=100)
    status_kesehatan = models.CharField(max_length=10, choices=STATUS_CHOICES)
    diagnosis = models.TextField(blank=True, null=True)
    pengobatan = models.TextField(blank=True, null=True)
    catatan_tindak_lanjut = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama_dokter} - {self.tanggal_pemeriksaan}"
    
class HealthCheckSchedule(models.Model):
    tanggal_pemeriksaan_selanjutnya = models.DateField()
    frekuensi_pemeriksaan_bulanan = models.PositiveIntegerField(default=3)  # default 3 bulan sekali

    def __str__(self):
        return f"Pemeriksaan berikutnya: {self.tanggal_pemeriksaan_selanjutnya} (Setiap {self.frekuensi_pemeriksaan_bulanan} bulan)"
