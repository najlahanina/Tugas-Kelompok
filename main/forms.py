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
        ('staff', 'Staff'),
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
    staff_role = forms.ChoiceField(choices=STAFF_ROLE_CHOICES, widget=forms.RadioSelect)
    staff_id = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

class UserProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100, label='Nama Depan')
    last_name = forms.CharField(max_length=100, label='Nama Belakang')
    middle_name = forms.CharField(max_length=100, required=False, label='Nama Tengah')
    phone_number = forms.CharField(max_length=20, label='Nomor Telepon')
    
    class Meta:
        model = UserProfile
        fields = ['middle_name', 'phone_number']
        
    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.role in ['animal_keeper', 'admin_staff', 'trainer']:
                self.fields['staff_id'] = forms.CharField(
                    max_length=10, 
                    disabled=True, 
                    required=False,
                    label='ID Staf',
                    initial=self.instance.staff_profile.staff_id if hasattr(self.instance, 'staff_profile') else ''
                )
            elif self.instance.role == 'veterinarian':
                self.fields['certification_number'] = forms.CharField(
                    max_length=100, 
                    disabled=True, 
                    required=False,
                    label='Nomor Sertifikasi Profesional',
                    initial=self.instance.vet_profile.certification_number if hasattr(self.instance, 'vet_profile') else ''
                )

class VisitorProfileUpdateForm(forms.ModelForm):
    """Form for updating visitor-specific profile information"""
    address = forms.CharField(widget=forms.Textarea, label='Alamat Lengkap')
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Tanggal Lahir'
    )
    
    class Meta:
        model = Visitor
        fields = []  
        
    def __init__(self, *args, **kwargs):
        super(VisitorProfileUpdateForm, self).__init__(*args, **kwargs)
        # Add profile fields to the form
        if self.instance and self.instance.pk:
            self.fields['address'].initial = self.instance.profile.address
            self.fields['birth_date'].initial = self.instance.profile.birth_date
            
    def save(self, commit=True):
        visitor = super(VisitorProfileUpdateForm, self).save(commit=False)
        # Update profile fields
        visitor.profile.address = self.cleaned_data['address']
        visitor.profile.birth_date = self.cleaned_data['birth_date']
        
        if commit:
            visitor.profile.save()
            visitor.save()
        return visitor

class VeterinarianProfileUpdateForm(forms.ModelForm):
    """Form for updating veterinarian-specific profile information"""
    SPECIALIZATION_CHOICES = Veterinarian.SPECIALIZATION_CHOICES
    
    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES, label='Spesialisasi')
    other_specialization = forms.CharField(
        max_length=100, 
        required=False,
        label='Spesialisasi Lainnya'
    )
    
    class Meta:
        model = Veterinarian
        fields = ['specialization', 'other_specialization']
        
    def clean(self):
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        other_specialization = cleaned_data.get('other_specialization')
        
        if specialization == 'other' and not other_specialization:
            self.add_error('other_specialization', 'Harap isi spesialisasi lainnya')
            
        return cleaned_data