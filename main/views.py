# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
import string
import hashlib
from datetime import datetime
from supabase_client import supabase
from .forms import (
    RoleSelectionForm, VisitorRegistrationForm, VeterinarianRegistrationForm,
    StaffRegistrationForm, UserProfileUpdateForm, VisitorProfileUpdateForm, VeterinarianProfileUpdateForm, PasswordChangeForm
)

def show_main(request):
    return render(request, 'main.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Query user from Supabase
            result = supabase.table('pengguna').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                if password == user_data['password']:
                    # Create session
                    request.session['username'] = username
                    request.session['user_data'] = user_data
                    
                    # Determine user role
                    role = get_user_role(username)
                    request.session['user_role'] = role
                    
                    return redirect('main:dashboard')
                else:
                    messages.error(request, 'Username atau password salah')
            else:
                messages.error(request, 'Username atau password salah')
                
        except Exception as e:
            messages.error(request, f'Error saat login: {str(e)}')
    
    return render(request, 'login.html')

def get_user_role(username):
    """Helper function to determine user role"""
    try:
        # Check if user is pengunjung
        result = supabase.table('pengunjung').select('username_p').eq('username_p', username).execute()
        if result.data and len(result.data) > 0:
            return 'visitor'
            
        # Check if user is dokter hewan
        result = supabase.table('dokter_hewan').select('username_dh').eq('username_dh', username).execute()
        if result.data and len(result.data) > 0:
            return 'veterinarian'
            
        # Check if user is penjaga hewan
        result = supabase.table('penjaga_hewan').select('username_jh').eq('username_jh', username).execute()
        if result.data and len(result.data) > 0:
            return 'animal_keeper'
            
        # Check if user is pelatih hewan
        result = supabase.table('pelatih_hewan').select('username_lh').eq('username_lh', username).execute()
        if result.data and len(result.data) > 0:
            return 'trainer'
            
        # Check if user is staf admin
        result = supabase.table('staf_admin').select('username_sa').eq('username_sa', username).execute()
        if result.data and len(result.data) > 0:
            return 'admin_staff'
            
        return 'unknown'
    except Exception as e:
        return 'unknown'

def logout_view(request):
    request.session.flush()
    return redirect('main:login')

def register_step1(request):
    """First step of registration - select role"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            request.session['selected_role'] = role
            return redirect('main:register_step2')
    else:
        form = RoleSelectionForm()
    
    return render(request, 'register_role.html', {'form': form})

def register_step2(request):
    """Second step of registration - fill form based on role"""
    role = request.session.get('selected_role')
    
    if not role:
        return redirect('main:register_step1')
    
    if role == 'visitor':
        return register_visitor(request)
    elif role == 'veterinarian':
        return register_veterinarian(request)
    elif role == 'staff':
        return register_staff(request, role)
    else:
        return redirect('main:register_step1')

def register_visitor(request):
    if request.method == 'POST':
        form = VisitorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                
                # Insert into PENGGUNA table
                pengguna_data = {
                    'username': username,
                    'email': form.cleaned_data['email'],
                    'password': password,
                    'nama_depan': form.cleaned_data['first_name'],
                    'nama_tengah': form.cleaned_data.get('middle_name', ''),
                    'nama_belakang': form.cleaned_data['last_name'],
                    'no_telepon': form.cleaned_data['phone_number']
                }
                
                pengguna_result = supabase.table('pengguna').insert(pengguna_data).execute()
                
                # Check if insert was successful
                if not pengguna_result.data:
                    raise Exception("Failed to insert into pengguna table")
                
                # Insert into PENGUNJUNG table
                pengunjung_data = {
                    'username_p': username,
                    'alamat': form.cleaned_data['address'],
                    'tgl_lahir': form.cleaned_data['birth_date'].isoformat()
                }
                
                pengunjung_result = supabase.table('pengunjung').insert(pengunjung_data).execute()
                
                # Check if insert was successful
                if not pengunjung_result.data:
                    raise Exception("Failed to insert into pengunjung table")
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('main:login')
                
            except Exception as e:
                messages.error(request, f'Error saat registrasi: {str(e)}')
                
                # Try to cleanup if pengguna was inserted but pengunjung failed
                try:
                    supabase.table('pengguna').delete().eq('username', username).execute()
                except:
                    pass
    else:
        form = VisitorRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'Pengunjung'})

def register_veterinarian(request):
    if request.method == 'POST':
        form = VeterinarianRegistrationForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                
                
                # Insert into PENGGUNA table
                pengguna_data = {
                    'username': username,
                    'email': form.cleaned_data['email'],
                    'password': password,
                    'nama_depan': form.cleaned_data['first_name'],
                    'nama_tengah': form.cleaned_data.get('middle_name', ''),
                    'nama_belakang': form.cleaned_data['last_name'],
                    'no_telepon': form.cleaned_data['phone_number']
                }
                
                pengguna_result = supabase.table('pengguna').insert(pengguna_data).execute()
                
                if not pengguna_result.data:
                    raise Exception("Failed to insert into pengguna table")
                
                # Insert into DOKTER_HEWAN table
                dokter_data = {
                    'username_dh': username,
                    'no_str': form.cleaned_data['certification_number']
                }
                
                dokter_result = supabase.table('dokter_hewan').insert(dokter_data).execute()
                
                if not dokter_result.data:
                    raise Exception("Failed to insert into dokter_hewan table")
                
                # Insert specializations
                specialization = (
                    form.cleaned_data.get('other_specialization')
                    if form.cleaned_data.get('specialization') == 'other'
                    else form.cleaned_data.get('specialization')
                )
                
                spesialisasi_data = {
                    'username_sh': username,
                    'nama_spesialisasi': specialization
                }
                
                spesialisasi_result = supabase.table('spesialisasi').insert(spesialisasi_data).execute()
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('main:login')
                
            except Exception as e:
                messages.error(request, f'Error saat registrasi: {str(e)}')
                
                # Cleanup on error
                try:
                    supabase.table('spesialisasi').delete().eq('username_sh', username).execute()
                    supabase.table('dokter_hewan').delete().eq('username_dh', username).execute()
                    supabase.table('pengguna').delete().eq('username', username).execute()
                except:
                    pass
    else:
        form = VeterinarianRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'Dokter Hewan'})

def register_staff(request, staff_role=None):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                staff_role = form.cleaned_data['staff_role']
                                
                # Insert into PENGGUNA table
                pengguna_data = {
                    'username': username,
                    'email': form.cleaned_data['email'],
                    'password': password,
                    'nama_depan': form.cleaned_data['first_name'],
                    'nama_tengah': form.cleaned_data.get('middle_name', ''),
                    'nama_belakang': form.cleaned_data['last_name'],
                    'no_telepon': form.cleaned_data['phone_number']
                }
                
                pengguna_result = supabase.table('pengguna').insert(pengguna_data).execute()
                
                if not pengguna_result.data:
                    raise Exception("Failed to insert into pengguna table")
                
                # Insert into appropriate staff table based on role
                staff_id = form.cleaned_data['staff_id']
                
                if staff_role == 'animal_keeper':
                    staff_data = {
                        'username_jh': username,
                        'id_staf': staff_id
                    }
                    staff_result = supabase.table('penjaga_hewan').insert(staff_data).execute()
                    
                elif staff_role == 'trainer':
                    staff_data = {
                        'username_lh': username,
                        'id_staf': staff_id
                    }
                    staff_result = supabase.table('pelatih_hewan').insert(staff_data).execute()
                    
                elif staff_role == 'admin_staff':
                    staff_data = {
                        'username_sa': username,
                        'id_staf': staff_id
                    }
                    staff_result = supabase.table('staf_admin').insert(staff_data).execute()
                                
                if not staff_result.data:
                    raise Exception(f"Failed to insert into {staff_role} table")
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('main:login')
                
            except Exception as e:
                messages.error(request, f'Error saat registrasi: {str(e)}')
                
                # Cleanup on error
                try:
                    if staff_role == 'animal_keeper':
                        supabase.table('penjaga_hewan').delete().eq('username_jh', username).execute()
                    elif staff_role == 'trainer':
                        supabase.table('pelatih_hewan').delete().eq('username_lh', username).execute()
                    elif staff_role == 'admin_staff':
                        supabase.table('staf_admin').delete().eq('username_sa', username).execute()
                    
                    supabase.table('pengguna').delete().eq('username', username).execute()
                except:
                    pass
    else:
        form = StaffRegistrationForm(initial={'staff_role': staff_role} if staff_role else {})
    
    return render(request, 'register.html', {
        'form': form, 
        'role': 'Staff',
    })

def generate_staff_id(request):
    """AJAX endpoint to generate staff ID"""
    role = request.GET.get('role')
    prefix_map = {
        'animal_keeper': 'PJH',
        'admin_staff': 'ADM',
        'trainer': 'PLP'
    }
    prefix = prefix_map.get(role, 'STF')
    random_suffix = ''.join(random.choices(string.digits, k=3))
    staff_id = f"{prefix}{random_suffix}"
    return JsonResponse({'staff_id': staff_id})

def login_required_custom(view_func):
    """Custom login required decorator using session"""
    def wrapper(request, *args, **kwargs):
        if 'username' not in request.session:
            return redirect('main:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_custom
def dashboard(request):
    """Dashboard view - displays different content based on user role"""
    try:
        username = request.session.get('username')
        user_data = request.session.get('user_data')
        role = request.session.get('user_role')
        
        # Get role-specific data
        role_data = {}
        visitor_data = {}
        
        if role == 'visitor':
            # Get visitor specific data
            visitor_result = supabase.table('pengunjung').select('*').eq('username_p', username).execute()
            if visitor_result.data:
                visitor_data = visitor_result.data[0]
                role_data = visitor_data
                # Convert tgl_lahir string to date object if exists
                if role_data.get('tgl_lahir'):
                    try:
                        from datetime import datetime
                        role_data['tgl_lahir'] = datetime.fromisoformat(role_data['tgl_lahir']).date()
                    except:
                        role_data['tgl_lahir'] = None
                
        elif role == 'veterinarian':
            # Get veterinarian specific data
            dokter_result = supabase.table('dokter_hewan').select('*').eq('username_dh', username).execute()
            if dokter_result.data:
                role_data = dokter_result.data[0]
                
            # Get specializations
            spesialisasi_result = supabase.table('spesialisasi').select('nama_spesialisasi').eq('username_sh', username).execute()
            if spesialisasi_result.data:
                role_data['specializations'] = [s['nama_spesialisasi'] for s in spesialisasi_result.data]
            else:
                role_data['specializations'] = []
                
        elif role == 'animal_keeper':
            # Get animal keeper specific data
            keeper_result = supabase.table('penjaga_hewan').select('*').eq('username_jh', username).execute()
            if keeper_result.data:
                role_data = keeper_result.data[0]
                
        elif role == 'trainer':
            # Get trainer specific data
            trainer_result = supabase.table('pelatih_hewan').select('*').eq('username_lh', username).execute()
            if trainer_result.data:
                role_data = trainer_result.data[0]
                
        elif role == 'admin_staff':
            # Get admin staff specific data
            admin_result = supabase.table('staf_admin').select('*').eq('username_sa', username).execute()
            if admin_result.data:
                role_data = admin_result.data[0]
        
        context = {
            'role': role,
            'user': user_data,
            'username': username,
            'role_data': role_data,
            'visitor_data': visitor_data,
        }
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error mengakses dashboard: {str(e)}')
        return redirect('main:login')


@login_required_custom
def profile_settings(request):
    """View for updating user profile information based on their role"""
    try:
        username = request.session.get('username')
        role = request.session.get('user_role')
        
        # Get current user data
        user_result = supabase.table('pengguna').select('*').eq('username', username).execute()
        if not user_result.data:
            messages.error(request, 'Profil pengguna tidak ditemukan')
            return redirect('main:dashboard')
            
        user_data = user_result.data[0]
        
        if request.method == 'POST':
            try:
                # Update PENGGUNA table
                update_data = {
                    'email': request.POST.get('email'),
                    'nama_depan': request.POST.get('first_name'),
                    'nama_belakang': request.POST.get('last_name'),
                    'nama_tengah': request.POST.get('middle_name', ''),
                    'no_telepon': request.POST.get('phone_number')
                }
                
                supabase.table('pengguna').update(update_data).eq('username', username).execute()
                
                # Update role-specific tables
                if role == 'visitor':
                    visitor_data = {
                        'alamat': request.POST.get('address'),
                        'tgl_lahir': request.POST.get('birth_date')
                    }
                    supabase.table('pengunjung').update(visitor_data).eq('username_p', username).execute()
                
                elif role == 'veterinarian':
                    # Ambil spesialisasi dari form
                    new_specialization = request.POST.get('specialization')
                    other_specialization = request.POST.get('other_specialization')

                    if new_specialization == 'other' and other_specialization:
                        new_specialization = other_specialization

                    if new_specialization:
                        # Hapus spesialisasi lama
                        supabase.table('spesialisasi').delete().eq('username_sh', username).execute()
                        # Simpan spesialisasi baru
                        spesialisasi_data = {
                            'username_sh': username,
                            'nama_spesialisasi': new_specialization
                        }
                        supabase.table('spesialisasi').insert(spesialisasi_data).execute()
                
                # Update session data
                request.session['user_data'] = {**user_data, **update_data}
                
                messages.success(request, 'Profil berhasil diperbarui')
                return redirect('main:dashboard')
                
            except Exception as e:
                messages.error(request, f'Error saat memperbarui profil: {str(e)}')
        
        # Get role-specific data for display
        role_data = {}
        if role == 'visitor':
            visitor_result = supabase.table('pengunjung').select('*').eq('username_p', username).execute()
            if visitor_result.data:
                role_data = visitor_result.data[0]
                
        elif role == 'veterinarian':
            dokter_result = supabase.table('dokter_hewan').select('*').eq('username_dh', username).execute()
            if dokter_result.data:
                role_data = dokter_result.data[0]
                
            # Get specializations
            spesialisasi_result = supabase.table('spesialisasi').select('nama_spesialisasi').eq('username_sh', username).execute()
            role_data['specializations'] = [s['nama_spesialisasi'] for s in spesialisasi_result.data]
        
        context = {
            'user_data': user_data,
            'role_data': role_data,
            'role': role,
            'username': username
        }
        
        return render(request, 'profile_settings.html', context)
        
    except Exception as e:
        messages.error(request, f'Error mengakses pengaturan profil: {str(e)}')
        return redirect('main:dashboard')

@login_required_custom
def change_password(request):
    """View for changing user password"""
    try:
        username = request.session.get('username')
        
        if request.method == 'POST':
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                current_password = form.cleaned_data['current_password']
                new_password = form.cleaned_data['new_password']
                
                try:
                    # Verify current password
                    result = supabase.table('pengguna').select('password').eq('username', username).execute()
                    
                    if not result.data or len(result.data) == 0:
                        messages.error(request, 'Pengguna tidak ditemukan')
                        return render(request, 'change_password.html', {'form': form})
                    
                    current_db_password = result.data[0]['password']
                    
                    if current_password != current_db_password:
                        messages.error(request, 'Password lama tidak benar')
                        return render(request, 'change_password.html', {'form': form})
                    
                    # Update password in Supabase
                    update_result = supabase.table('pengguna').update({
                        'password': new_password
                    }).eq('username', username).execute()
                    
                    if update_result.data:
                        # Update session data
                        user_data = request.session.get('user_data')
                        if user_data:
                            user_data['password'] = new_password
                            request.session['user_data'] = user_data
                        
                        messages.success(request, 'Password berhasil diubah')
                        return redirect('main:dashboard')
                    else:
                        messages.error(request, 'Gagal mengubah password')
                        
                except Exception as e:
                    messages.error(request, f'Error saat mengubah password: {str(e)}')
            else:
                # Display form errors
                for field_name, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field_name}: {error}')
        else:
            form = PasswordChangeForm()
        
        return render(request, 'change_password.html', {'form': form})
        
    except Exception as e:
        messages.error(request, f'Error mengakses halaman ubah password: {str(e)}')
        return redirect('main:dashboard')