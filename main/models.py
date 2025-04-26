from django.db import models
from django.contrib.auth.models import User

# User profile model to extend the built-in User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # The role choices
    ROLE_CHOICES = (
        ('visitor', 'Pengunjung'),
        ('veterinarian', 'Dokter Hewan'),
        ('animal_keeper', 'Penjaga Hewan'),
        ('admin_staff', 'Staf Administrasi'),
        ('trainer', 'Pelatih Pertunjukan'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# Visitor specific profile
class Visitor(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='visitor_profile')
    is_adopter = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Pengunjung: {self.profile.user.username}"

# Veterinarian specific profile
class Veterinarian(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='vet_profile')
    certification_number = models.CharField(max_length=100)
    
    # Specialization choices
    SPECIALIZATION_CHOICES = (
        ('large_mammals', 'Mamalia Besar'),
        ('reptiles', 'Reptil'),
        ('exotic_birds', 'Burung Eksotis'),
        ('primates', 'Primata'),
        ('other', 'Lainnya'),
    )
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    other_specialization = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Dokter Hewan: {self.profile.user.username}"

# Staff model (for animal keeper, admin staff, and trainer)
class Staff(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='staff_profile')
    
    # Staff ID type prefixes
    STAFF_TYPE_PREFIXES = {
        'animal_keeper': 'PJH',
        'admin_staff': 'ADM',
        'trainer': 'PLP',
    }
    
    staff_id = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.profile.get_role_display()}: {self.profile.user.username} ({self.staff_id})"