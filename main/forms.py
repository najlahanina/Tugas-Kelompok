from django import forms
from django.core.exceptions import ValidationError
from supabase_client import supabase
import re

class BaseRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password2 = forms.CharField(
        label='Konfirmasi Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=50, 
        required=True,
        label='Nama Depan',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        max_length=50, 
        required=False,
        label='Nama Tengah',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50, 
        required=True,
        label='Nama Belakang',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        label='Nomor Telepon',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Check if username already exists in Supabase
        try:
            result = supabase.table('pengguna').select('username').eq('username', username).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('Username sudah digunakan.')
        except Exception as e:
            # If there's an error connecting to Supabase, allow the form to proceed
            # The actual insert will handle the constraint
            pass
            
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check if email already exists in Supabase
        try:
            result = supabase.table('pengguna').select('email').eq('email', email).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('Email sudah digunakan.')
        except Exception as e:
            # If there's an error connecting to Supabase, allow the form to proceed
            pass
            
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        
        # Basic phone number validation
        if not re.match(r'^[\d\-\+\(\)\s]+$', phone):
            raise ValidationError('Nomor telepon tidak valid.')
            
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Password tidak cocok.')
                
        return cleaned_data

class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = (
        ('visitor', 'Pengunjung'),
        ('veterinarian', 'Dokter Hewan'),
        ('staff', 'Staff'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        label="Pilih Peran",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

class VisitorRegistrationForm(BaseRegistrationForm):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
        required=True,
        max_length=200,
        label='Alamat Lengkap'
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=True,
        label='Tanggal Lahir'
    )
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        from datetime import date
        
        # Check if birth date is not in the future
        if birth_date > date.today():
            raise ValidationError('Tanggal lahir tidak boleh di masa depan.')
            
        # Check minimum age (optional)
        age = date.today().year - birth_date.year
        if age < 5:
            raise ValidationError('Usia minimal 5 tahun.')
            
        return birth_date

class VeterinarianRegistrationForm(BaseRegistrationForm):
    certification_number = forms.CharField(
        max_length=50, 
        required=True,
        label='Nomor STR (Surat Tanda Registrasi)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    SPECIALIZATION_CHOICES = (
        ('Mamalia Besar', 'Mamalia Besar'),
        ('Reptil', 'Reptil'),
        ('Burung Eksotis', 'Burung Eksotis'),
        ('Primata', 'Primata'),
        ('other', 'Lainnya'),
    )
    specialization = forms.ChoiceField(
        choices=SPECIALIZATION_CHOICES,
        label='Spesialisasi',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    other_specialization = forms.CharField(
        max_length=100, 
        required=False,
        label='Spesialisasi Lainnya',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_certification_number(self):
        cert_number = self.cleaned_data['certification_number']
        
        # Check if certification number already exists
        try:
            result = supabase.table('dokter_hewan').select('no_str').eq('no_str', cert_number).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('Nomor STR sudah terdaftar.')
        except Exception as e:
            pass
            
        return cert_number
    
    def clean(self):
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        other_specialization = cleaned_data.get('other_specialization')
        
        if specialization == 'other' and not other_specialization:
            raise ValidationError('Harap isi spesialisasi lainnya jika memilih "Lainnya".')
            
        return cleaned_data

class StaffRegistrationForm(BaseRegistrationForm):
    STAFF_ROLE_CHOICES = (
        ('animal_keeper', 'Penjaga Hewan (PJHXXX)'),
        ('admin_staff', 'Staf Administrasi (ADMXXX)'),
        ('trainer', 'Pelatih Pertunjukan (PLPXXX)'),
    )
    staff_role = forms.ChoiceField(
        choices=STAFF_ROLE_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Jenis Staff'
    )
    staff_id = forms.CharField(
        max_length=10, 
        required=False, 
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        label='ID Staff'
    )
    
    def clean_staff_id(self):
        staff_id = self.cleaned_data['staff_id']
        
        if not staff_id:
            raise ValidationError('ID Staff harus diisi.')
            
        # Check if staff ID already exists in any staff table
        try:
            # Check penjaga_hewan
            result = supabase.table('penjaga_hewan').select('id_staf').eq('id_staf', staff_id).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('ID Staff sudah digunakan.')
                
            # Check pelatih_hewan
            result = supabase.table('pelatih_hewan').select('id_staf').eq('id_staf', staff_id).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('ID Staff sudah digunakan.')
                
            # Check staf_admin
            result = supabase.table('staf_admin').select('id_staf').eq('id_staf', staff_id).execute()
            if result.data and len(result.data) > 0:
                raise ValidationError('ID Staff sudah digunakan.')
                
        except Exception as e:
            pass
            
        return staff_id

class UserProfileUpdateForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    first_name = forms.CharField(
        max_length=50, 
        label='Nama Depan',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50, 
        label='Nama Belakang',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        max_length=50, 
        required=False, 
        label='Nama Tengah',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        label='Nomor Telepon',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        if self.username:
            # Check if email is used by other users (excluding current user)
            try:
                result = supabase.table('pengguna').select('email', 'username').eq('email', email).execute()
                if result.data:
                    for user in result.data:
                        if user['username'] != self.username:
                            raise ValidationError('Email sudah digunakan oleh pengguna lain.')
            except Exception as e:
                pass
                
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        
        # Basic phone number validation
        if not re.match(r'^[\d\-\+\(\)\s]+$', phone):
            raise ValidationError('Nomor telepon tidak valid.')
            
        return phone

class VisitorProfileUpdateForm(forms.Form):
    """Form for updating visitor-specific profile information"""
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
        label='Alamat Lengkap',
        max_length=200
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Tanggal Lahir'
    )
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        from datetime import date
        
        # Check if birth date is not in the future
        if birth_date > date.today():
            raise ValidationError('Tanggal lahir tidak boleh di masa depan.')
            
        return birth_date

class VeterinarianProfileUpdateForm(forms.Form):
    """Form for updating veterinarian-specific profile information"""
    SPECIALIZATION_CHOICES = (
        ('Mamalia Besar', 'Mamalia Besar'),
        ('Reptil', 'Reptil'),
        ('Burung Eksotis', 'Burung Eksotis'),
        ('Primata', 'Primata'),
        ('other', 'Lainnya'),
    )
    
    certification_number = forms.CharField(
        max_length=50,
        label='Nomor STR (Surat Tanda Registrasi)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    specialization = forms.ChoiceField(
        choices=SPECIALIZATION_CHOICES, 
        label='Spesialisasi',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    other_specialization = forms.CharField(
        max_length=100, 
        required=False,
        label='Spesialisasi Lainnya',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(VeterinarianProfileUpdateForm, self).__init__(*args, **kwargs)
    
    def clean_certification_number(self):
        cert_number = self.cleaned_data['certification_number']
        
        if self.username:
            # Check if certification number is used by other veterinarians
            try:
                result = supabase.table('dokter_hewan').select('no_str', 'username_dh').eq('no_str', cert_number).execute()
                if result.data:
                    for vet in result.data:
                        if vet['username_dh'] != self.username:
                            raise ValidationError('Nomor STR sudah digunakan oleh dokter hewan lain.')
            except Exception as e:
                pass
                
        return cert_number
    
    def clean(self):
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        other_specialization = cleaned_data.get('other_specialization')
        
        if specialization == 'other' and not other_specialization:
            raise ValidationError('Harap isi spesialisasi lainnya jika memilih "Lainnya".')
            
        return cleaned_data

class PasswordChangeForm(forms.Form):
    """Form for changing user password"""
    current_password = forms.CharField(
        label='Password Lama',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label='Password Baru',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        label='Konfirmasi Password Baru',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('Password baru dan konfirmasi password tidak cocok.')
                
        return cleaned_data