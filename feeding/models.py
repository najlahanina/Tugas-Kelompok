from django.db import models
from django.contrib.auth.models import User

class FeedingSchedule(models.Model):
    STATUS_CHOICES = [
        ('Menunggu Diberikan', 'Menunggu Diberikan'),
        ('Selesai Diberikan', 'Selesai Diberikan'),
    ]

    jenis_pakan = models.CharField(max_length=100)
    jumlah_pakan = models.PositiveIntegerField()
    jadwal = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Menunggu Diberikan')
    penjaga = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.jenis_pakan} - {self.jumlah_pakan}g ({self.status})"
