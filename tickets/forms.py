# forms tickets
from django import forms
from django.utils import timezone
from supabase_client import supabase

def get_attractions_list():
    """Get attractions list from Supabase"""
    try:
        response = supabase.table('atraksi').select('nama_atraksi').execute()
        return [(item['nama_atraksi'], item['nama_atraksi']) for item in response.data]
    except Exception as e:
        print(f"Error loading attractions: {e}")
        return []

class ReservasiForm(forms.Form):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    nama_atraksi = forms.ChoiceField(choices=[], required=True)
    tanggal_kunjungan = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    jumlah_tiket = forms.IntegerField(min_value=1, required=True)

    def __init__(self, *args, **kwargs):
        super(ReservasiForm, self).__init__(*args, **kwargs)
        
        # Set minimum date to today
        self.fields['tanggal_kunjungan'].widget.attrs['min'] = timezone.now().date().isoformat()
        
        # Get attractions from database
        try:
            atraksi_choices = get_attractions_list()
            self.fields['nama_atraksi'].choices = [('', 'Pilih Atraksi')] + atraksi_choices
            
        except Exception as e:
            print(f"Error loading attractions: {e}")
            # Fallback choices
            self.fields['nama_atraksi'].choices = [
                ('', 'Pilih Atraksi'),
                ('Pertunjukan lumba-lumba', 'Pertunjukan lumba-lumba'),
                ('Feeding time harimau', 'Feeding time harimau'),
                ('Bird show', 'Bird show'),
            ]

    def clean_tanggal_kunjungan(self):
        tanggal = self.cleaned_data['tanggal_kunjungan']
        if tanggal < timezone.now().date():
            raise forms.ValidationError("Tanggal kunjungan tidak boleh di masa lalu.")
        return tanggal

    def clean(self):
        cleaned_data = super().clean()
        nama_atraksi = cleaned_data.get('nama_atraksi')
        tanggal_kunjungan = cleaned_data.get('tanggal_kunjungan')
        jumlah_tiket = cleaned_data.get('jumlah_tiket')

        # Check attraction capacity if all fields are valid
        if nama_atraksi and tanggal_kunjungan and jumlah_tiket:
            try:
                # Get attraction capacity - now using nama_atraksi directly as it references fasilitas.nama
                capacity_result = supabase.table('fasilitas').select('kapasitas_max').eq('nama', nama_atraksi).execute()
                
                if capacity_result.data:
                    max_capacity = capacity_result.data[0]['kapasitas_max']
                    
                    # Check existing reservations for the same date - using nama_fasilitas
                    existing_result = supabase.table('reservasi').select('jumlah_tiket').eq('nama_fasilitas', nama_atraksi).eq('tanggal_kunjungan', str(tanggal_kunjungan)).neq('status', 'Dibatalkan').execute()
                    
                    total_reserved = sum(item['jumlah_tiket'] for item in existing_result.data) if existing_result.data else 0
                    available_capacity = max_capacity - total_reserved
                    
                    # if jumlah_tiket > available_capacity:
                    #     raise forms.ValidationError(
                    #         f"Kapasitas tidak mencukupi. Tersisa {available_capacity} tiket untuk tanggal ini."
                    #     )
                        
            except Exception as e:
                print(f"Error checking capacity: {e}")
                # Don't block the form if capacity check fails
                pass

        return cleaned_data


class ReservasiEditForm(forms.Form):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    jumlah_tiket = forms.IntegerField(min_value=1, required=True)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, disabled=True)
    
    # Read-only fields for display
    username_p = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Username"
    )
    nama_fasilitas = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Nama Fasilitas"
    )
    tanggal_kunjungan = forms.DateField(
        widget=forms.DateInput(attrs={'readonly': 'readonly', 'type': 'date'}),
        required=False,
        label="Tanggal Kunjungan"
    )

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.get('initial', {})
        super(ReservasiEditForm, self).__init__(*args, **kwargs)
        
        # Set initial values for read-only fields
        if initial_data:
            self.fields['username_p'].initial = initial_data.get('username_p', '')
            self.fields['nama_fasilitas'].initial = initial_data.get('nama_fasilitas', '')
            self.fields['tanggal_kunjungan'].initial = initial_data.get('tanggal_kunjungan', '')
            self.fields['jumlah_tiket'].initial = initial_data.get('jumlah_tiket', 1)
            self.fields['status'].initial = initial_data.get('status', 'Terjadwal')

    def clean_jumlah_tiket(self):
        jumlah_tiket = self.cleaned_data['jumlah_tiket']
        if jumlah_tiket < 1:
            raise forms.ValidationError("Jumlah tiket minimal 1.")
        
        # Additional capacity validation during edit
        nama_fasilitas = self.initial.get('nama_fasilitas')
        tanggal_kunjungan = self.initial.get('tanggal_kunjungan')
        username_p = self.initial.get('username_p')
        current_jumlah = self.initial.get('jumlah_tiket', 0)
        
        if nama_fasilitas and tanggal_kunjungan:
            try:
                # Get facility capacity
                capacity_result = supabase.table('fasilitas').select('kapasitas_max').eq('nama', nama_fasilitas).execute()
                
                if capacity_result.data:
                    max_capacity = capacity_result.data[0]['kapasitas_max']
                    
                    # Get existing reservations excluding current reservation
                    existing_result = supabase.table('reservasi').select('jumlah_tiket').eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', str(tanggal_kunjungan)).neq('status', 'Dibatalkan').execute()
                    
                    # Calculate total reserved excluding current reservation
                    total_reserved = 0
                    for item in existing_result.data:
                        total_reserved += item['jumlah_tiket']
                    
                    # Subtract current reservation amount to get actual available capacity
                    total_reserved -= current_jumlah
                    available_capacity = max_capacity - total_reserved
                    
                    # if jumlah_tiket > available_capacity:
                    #     raise forms.ValidationError(
                    #         f"Kapasitas tidak mencukupi. Tersisa {available_capacity} tiket untuk tanggal ini."
                    #     )
                        
            except Exception as e:
                print(f"Error checking capacity during edit: {e}")
                # Don't block the form if capacity check fails
                pass
        
        return jumlah_tiket

def get_wahana_list():
    """Get wahana list from Supabase"""
    try:
        response = supabase.table('wahana').select('nama_wahana').execute()
        return [(item['nama_wahana'], item['nama_wahana']) for item in response.data]
    except Exception as e:
        print(f"Error loading wahana: {e}")
        return []

class ReservasiWahanaForm(forms.Form):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    nama_wahana = forms.ChoiceField(choices=[], required=True, label="Nama Wahana")
    tanggal_kunjungan = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Tanggal Kunjungan"
    )
    jumlah_tiket = forms.IntegerField(min_value=1, required=True, label="Jumlah Tiket")

    def __init__(self, *args, **kwargs):
        super(ReservasiWahanaForm, self).__init__(*args, **kwargs)
        
        # Set minimum date to today
        self.fields['tanggal_kunjungan'].widget.attrs['min'] = timezone.now().date().isoformat()
        
        # Get wahana from database
        try:
            wahana_choices = get_wahana_list()
            self.fields['nama_wahana'].choices = [('', 'Pilih Wahana')] + wahana_choices
            
        except Exception as e:
            print(f"Error loading wahana: {e}")
            # Fallback choices
            self.fields['nama_wahana'].choices = [
                ('', 'Pilih Wahana'),
                ('Roller Coaster', 'Roller Coaster'),
                ('Bianglala', 'Bianglala'),
                ('Komidi Putar', 'Komidi Putar'),
            ]

    def clean_tanggal_kunjungan(self):
        tanggal = self.cleaned_data['tanggal_kunjungan']
        if tanggal < timezone.now().date():
            raise forms.ValidationError("Tanggal kunjungan tidak boleh di masa lalu.")
        return tanggal

    def clean(self):
        cleaned_data = super().clean()
        nama_wahana = cleaned_data.get('nama_wahana')
        tanggal_kunjungan = cleaned_data.get('tanggal_kunjungan')
        jumlah_tiket = cleaned_data.get('jumlah_tiket')

        # Check wahana capacity if all fields are valid
        if nama_wahana and tanggal_kunjungan and jumlah_tiket:
            try:
                # Get wahana capacity - using nama_wahana as it references fasilitas.nama
                capacity_result = supabase.table('fasilitas').select('kapasitas_max').eq('nama', nama_wahana).execute()
                
                if capacity_result.data:
                    max_capacity = capacity_result.data[0]['kapasitas_max']
                    
                    # Check existing reservations for the same date
                    existing_result = supabase.table('reservasi').select('jumlah_tiket').eq('nama_fasilitas', nama_wahana).eq('tanggal_kunjungan', str(tanggal_kunjungan)).neq('status', 'Dibatalkan').execute()
                    
                    total_reserved = sum(item['jumlah_tiket'] for item in existing_result.data) if existing_result.data else 0
                    available_capacity = max_capacity - total_reserved
                    
                    if jumlah_tiket > available_capacity:
                        raise forms.ValidationError(
                            f"Kapasitas tidak mencukupi. Tersisa {available_capacity} tiket untuk tanggal ini."
                        )
                        
            except Exception as e:
                print(f"Error checking capacity: {e}")
                # Don't block the form if capacity check fails
                pass

        return cleaned_data


class ReservasiWahanaEditForm(forms.Form):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    jumlah_tiket = forms.IntegerField(min_value=1, required=True, label="Jumlah Tiket")
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, disabled=True, label="Status")
    
    # Read-only fields for display
    username_p = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Username"
    )
    nama_fasilitas = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Nama Wahana"
    )
    tanggal_kunjungan = forms.DateField(
        widget=forms.DateInput(attrs={'readonly': 'readonly', 'type': 'date'}),
        required=False,
        label="Tanggal Kunjungan"
    )

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.get('initial', {})
        super(ReservasiWahanaEditForm, self).__init__(*args, **kwargs)
        
        # Set initial values for read-only fields
        if initial_data:
            self.fields['username_p'].initial = initial_data.get('username_p', '')
            self.fields['nama_fasilitas'].initial = initial_data.get('nama_fasilitas', '')
            self.fields['tanggal_kunjungan'].initial = initial_data.get('tanggal_kunjungan', '')
            self.fields['jumlah_tiket'].initial = initial_data.get('jumlah_tiket', 1)
            self.fields['status'].initial = initial_data.get('status', 'Terjadwal')

    def clean_jumlah_tiket(self):
        jumlah_tiket = self.cleaned_data['jumlah_tiket']
        if jumlah_tiket < 1:
            raise forms.ValidationError("Jumlah tiket minimal 1.")
        
        # Additional capacity validation during edit
        nama_fasilitas = self.initial.get('nama_fasilitas')
        tanggal_kunjungan = self.initial.get('tanggal_kunjungan')
        username_p = self.initial.get('username_p')
        current_jumlah = self.initial.get('jumlah_tiket', 0)
        
        if nama_fasilitas and tanggal_kunjungan:
            try:
                # Get facility capacity
                capacity_result = supabase.table('fasilitas').select('kapasitas_max').eq('nama', nama_fasilitas).execute()
                
                if capacity_result.data:
                    max_capacity = capacity_result.data[0]['kapasitas_max']
                    
                    # Get existing reservations excluding current reservation
                    existing_result = supabase.table('reservasi').select('jumlah_tiket').eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', str(tanggal_kunjungan)).neq('status', 'Dibatalkan').execute()
                    
                    # Calculate total reserved excluding current reservation
                    total_reserved = 0
                    for item in existing_result.data:
                        total_reserved += item['jumlah_tiket']
                    
                    # Subtract current reservation amount to get actual available capacity
                    total_reserved -= current_jumlah
                    available_capacity = max_capacity - total_reserved
                    
                    if jumlah_tiket > available_capacity:
                        raise forms.ValidationError(
                            f"Kapasitas tidak mencukupi. Tersisa {available_capacity} tiket untuk tanggal ini."
                        )
                        
            except Exception as e:
                print(f"Error checking capacity during edit: {e}")
                # Don't block the form if capacity check fails
                pass
        
        return jumlah_tiket
    
class AdminReservasiEditForm(forms.Form):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    jumlah_tiket = forms.IntegerField(min_value=1, required=True)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True)
    
    # Read-only fields for display
    username_p = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Username Pengunjung"
    )
    nama_atraksi = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
        label="Nama Atraksi"
    )
    tanggal_kunjungan = forms.DateField(
        widget=forms.DateInput(attrs={'readonly': 'readonly', 'type': 'date'}),
        required=False,
        label="Tanggal Kunjungan"
    )

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.get('initial', {})
        super(AdminReservasiEditForm, self).__init__(*args, **kwargs)
        
        # Set initial values for read-only fields
        if initial_data:
            self.fields['username_p'].initial = initial_data.get('username_p', '')
            self.fields['nama_atraksi'].initial = initial_data.get('nama_atraksi', '')
            self.fields['tanggal_kunjungan'].initial = initial_data.get('tanggal_kunjungan', '')
            self.fields['jumlah_tiket'].initial = initial_data.get('jumlah_tiket', 1)
            self.fields['status'].initial = initial_data.get('status', 'Terjadwal')

    def clean_jumlah_tiket(self):
        jumlah_tiket = self.cleaned_data['jumlah_tiket']
        if jumlah_tiket < 1:
            raise forms.ValidationError("Jumlah tiket minimal 1.")
        return jumlah_tiket

    def clean(self):
        cleaned_data = super().clean()
        nama_atraksi = self.initial.get('nama_atraksi')
        tanggal_kunjungan = self.initial.get('tanggal_kunjungan')
        jumlah_tiket = cleaned_data.get('jumlah_tiket')
        username_p = self.initial.get('username_p')

        # Check capacity when admin edits ticket count
        if nama_atraksi and tanggal_kunjungan and jumlah_tiket:
            try:
                # Get attraction capacity
                capacity_result = supabase.table('fasilitas').select('kapasitas_max').eq('nama', nama_atraksi).execute()
                
                if capacity_result.data:
                    max_capacity = capacity_result.data[0]['kapasitas_max']
                    
                    # Check existing reservations for the same date (excluding current reservation)
                    existing_result = supabase.table('reservasi').select('jumlah_tiket').eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', str(tanggal_kunjungan)).neq('status', 'Dibatalkan').neq('username_p', username_p).execute()
                    
                    total_reserved = sum(item['jumlah_tiket'] for item in existing_result.data) if existing_result.data else 0
                    available_capacity = max_capacity - total_reserved
                    
                    if jumlah_tiket > available_capacity:
                        raise forms.ValidationError(
                            f"Kapasitas tidak mencukupi. Tersisa {available_capacity} tiket untuk tanggal ini."
                        )
                        
            except Exception as e:
                print(f"Error checking capacity: {e}")
                # Don't block the form if capacity check fails
                pass

        return cleaned_data