from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Visitor, Veterinarian, Staff

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    middle_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'middle_name', 'last_name', 'email')

class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = (
        ('visitor', 'Pengunjung'),
        ('veterinarian', 'Dokter Hewan'),
        ('animal_keeper', 'Penjaga Hewan'),
        ('admin_staff', 'Staf Administrasi'),
        ('trainer', 'Pelatih Pertunjukan'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Pilih Peran")

class VisitorRegistrationForm(UserRegistrationForm):
    address = forms.CharField(widget=forms.Textarea, required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    
    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ('address', 'birth_date')

class VeterinarianRegistrationForm(UserRegistrationForm):
    certification_number = forms.CharField(max_length=100, required=True)
    
    SPECIALIZATION_CHOICES = (
        ('large_mammals', 'Mamalia Besar'),
        ('reptiles', 'Reptil'),
        ('exotic_birds', 'Burung Eksotis'),
        ('primates', 'Primata'),
        ('other', 'Lainnya'),
    )
    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES)
    other_specialization = forms.CharField(max_length=100, required=False)

class StaffRegistrationForm(UserRegistrationForm):
    STAFF_ROLE_CHOICES = (
        ('animal_keeper', 'Penjaga Hewan (PJHXXX)'),
        ('admin_staff', 'Staf Administrasi (ADMXXX)'),
        ('trainer', 'Pelatih Pertunjukan (PLPXXX)'),
    )
    staff_role = forms.ChoiceField(choices=STAFF_ROLE_CHOICES)
    staff_id = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))