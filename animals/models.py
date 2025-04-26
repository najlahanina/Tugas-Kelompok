from django.db import models

class Animal(models.Model):
    STATUS_CHOICES = [
        ('Sehat', 'Sehat'),
        ('Sakit', 'Sakit'),
        ('Dalam Pemantauan', 'Dalam Pemantauan'),
    ]
    
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Individu")
    species = models.CharField(max_length=100, verbose_name="Spesies")
    origin = models.CharField(max_length=100, verbose_name="Asal Hewan")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Lahir")
    health_status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status Kesehatan")
    habitat = models.ForeignKey('habitats.Habitat', on_delete=models.SET_NULL, null=True, verbose_name="Habitat")
    photo_url = models.URLField(blank=True, null=True, verbose_name="URL Foto Satwa")
    
    def __str__(self):
        return f"{self.name} ({self.species})" if self.name else self.species
    
    class Meta:
        verbose_name = "Satwa"
        verbose_name_plural = "Data Satwa"