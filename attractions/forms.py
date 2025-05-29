from django import forms
from supabase_client import supabase

class AtraksiForm(forms.Form):
    nama_atraksi = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Nama atraksi'
        })
    )

    lokasi = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Lokasi atraksi'
        })
    )

    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]',
            'placeholder': 'Kapasitas maksimum'
        })
    )

    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]'
        })
    )

    pelatih = forms.MultipleChoiceField(
        choices=[],  
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2 ml-1'
        }),
        required=False
    )

    hewan = forms.MultipleChoiceField(
        choices=[],  
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2 ml-1'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate pelatih choices from database
        try:
            pelatih_result = supabase.table('pelatih_hewan').select('''
                username_lh,
                pengguna!inner(
                    nama_depan,
                    nama_belakang
                )
            ''').execute()
            
            pelatih_choices = []
            for pelatih in pelatih_result.data:
                pengguna = pelatih['pengguna']
                full_name = f"{pengguna['nama_depan']} {pengguna['nama_belakang']}"
                pelatih_choices.append((pelatih['username_lh'], full_name))
            
            self.fields['pelatih'].choices = pelatih_choices
        except Exception as e:
            self.fields['pelatih'].choices = []

        # Populate hewan choices from database
        try:
            hewan_result = supabase.table('hewan').select('id, nama, spesies').execute()
            
            hewan_choices = []
            for hewan in hewan_result.data:
                display_name = hewan['nama'] if hewan['nama'] else hewan['spesies']
                hewan_choices.append((hewan['id'], display_name))
            
            self.fields['hewan'].choices = hewan_choices
        except Exception as e:
            self.fields['hewan'].choices = []


class EditAtraksiForm(forms.Form):
    kapasitas_max = forms.IntegerField(
        label='Kapasitas Maksimum',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]'
        })
    )
    jadwal = forms.TimeField(
        label='Jadwal Atraksi',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full border border-gray-300 px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-[#586132] focus:border-[#586132]'
        })
    )
    pelatih_choices = []
    try:
        pelatih_result = supabase.table('pelatih_hewan').select('username_lh').execute()
        pengguna_result = supabase.table('pengguna').select('username, nama_depan, nama_belakang').execute()
        pengguna_map = {p['username']: f"{p['nama_depan']} {p['nama_belakang']}" for p in pengguna_result.data}
        pelatih_choices = [(p['username_lh'], pengguna_map.get(p['username_lh'], p['username_lh'])) for p in pelatih_result.data]
    except Exception as e:
        print(f"Error loading pelatih choices: {e}")
    pelatih = forms.MultipleChoiceField(
        label='Pelatih Pertunjukan',
        choices=pelatih_choices,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2 ml-1'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pelatih_choices = []
        try:
            pelatih_result = supabase.table('pelatih_hewan').select('username_lh').execute()
            pengguna_result = supabase.table('pengguna').select('username, nama_depan, nama_belakang').execute()
            pengguna_map = {p['username']: f"{p['nama_depan']} {p['nama_belakang']}" for p in pengguna_result.data}
            pelatih_choices = [(p['username_lh'], pengguna_map.get(p['username_lh'], p['username_lh'])) for p in pelatih_result.data]
            self.fields['pelatih'].choices = pelatih_choices
        except Exception as e:
            print(f"Error reloading pelatih choices: {e}")

class WahanaForm(forms.Form):
    nama_wahana = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Nama Wahana',
        })
    )
    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Kapasitas Maksimal',
        })
    )
    jadwal = forms.TimeField(
        label='Jadwal Wahana',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
        })
    )
    peraturan = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'rows': 4,
            'placeholder': 'Peraturan',
        }),
        required=True
    )


class EditWahanaForm(forms.Form):
    kapasitas_max = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
            'placeholder': 'Kapasitas Maksimal',
        })
    )
    jadwal = forms.TimeField(
        label='Jadwal Wahana',
        widget=forms.TimeInput(format='%H:%M', attrs={
            'type': 'time',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300',
        })
    )

    def __init__(self, *args, **kwargs):
        # Extract initial data if passed
        initial_data = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)
        
        # Set initial values if available
        if 'peraturan' in initial_data:
            self.fields['peraturan'].initial = initial_data['peraturan']