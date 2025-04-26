from django.db import models

class Habitat(models.Model):
    name = models.CharField(
        max_length=100, 
        verbose_name="Nama Habitat", 
        default="Unknown Habitat"  # <-- tambah default
    )
    area = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Luas Area", 
        default=0.00
    )
    max_capacity = models.IntegerField(
        verbose_name="Kapasitas Maksimal", 
        default=0  # <-- tambah default
    )
    environment_status = models.TextField(
        verbose_name="Status Lingkungan", 
        default="Unknown"
    )
    
    def __str__(self):
        return self.name
    
    def get_animals_count(self):
        return self.animal_set.count()
    
    class Meta:
        verbose_name = "Habitat"
        verbose_name_plural = "Habitats"