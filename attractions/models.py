# facilities/models.py

from django.db import models
from django.contrib.auth.models import User
from animals.models import Animal

class Fasilitas(models.Model):
    nama = models.CharField(max_length=50, primary_key=True)
    jadwal = models.DateTimeField()
    kapasitas_max = models.IntegerField()

    def __str__(self):
        return self.nama

class Atraksi(models.Model):
    nama_atraksi = models.OneToOneField(Fasilitas, on_delete=models.CASCADE, primary_key=True)
    lokasi = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_atraksi.nama

class Wahana(models.Model):
    nama_wahana = models.OneToOneField(Fasilitas, on_delete=models.CASCADE, primary_key=True)
    peraturan = models.TextField()

    def __str__(self):
        return self.nama_wahana.nama

class Berpartisipasi(models.Model):
    nama_fasilitas = models.ForeignKey(Fasilitas, on_delete=models.CASCADE)
    id_hewan = models.ForeignKey(Animal, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nama_fasilitas', 'id_hewan')

class JadwalPenugasan(models.Model):
    username_lh = models.CharField(max_length=50)  # FK ke Pelatih (UserProfile role = 'trainer')
    tgl_penugasan = models.DateTimeField()
    nama_atraksi = models.ForeignKey(Atraksi, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('username_lh', 'tgl_penugasan')
