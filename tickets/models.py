from django.db import models
from django.contrib.auth.models import User
from attractions.models import Atraksi

class Reservasi(models.Model):
    username_p = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservasi')
    nama_atraksi = models.ForeignKey(Atraksi, on_delete=models.CASCADE, related_name='reservasi')
    tanggal_kunjungan = models.DateField()
    jumlah_tiket = models.IntegerField(null=False)
    
    STATUS_CHOICES = (
        ('terjadwal', 'Terjadwal'),
        ('dibatalkan', 'Dibatalkan'),
        ('selesai', 'Selesai'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=False)
    
    class Meta:
        unique_together = ('username_p', 'nama_atraksi', 'tanggal_kunjungan')
        
    def __str__(self):
        return f"{self.username_p.username} - {self.nama_atraksi} - {self.tanggal_kunjungan}"