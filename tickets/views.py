# views tickets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ReservasiForm, ReservasiEditForm, AdminReservasiEditForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
from supabase_client import supabase
from main.views import login_required_custom, get_user_role  # Import from main views
import uuid
from datetime import datetime

@login_required_custom
def tambah_reservasi(request):
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            try:
                # Get attraction details
                attraction_result = supabase.table('atraksi').select('*').eq('nama_atraksi', cd['nama_atraksi']).execute()
                
                if not attraction_result.data:
                    messages.error(request, "Atraksi tidak ditemukan")
                    return redirect('tickets:tambah_reservasi')
                
                attraction = attraction_result.data[0]
                
                # Get facility details 
                facility_result = supabase.table('fasilitas').select('*').eq('nama', cd['nama_atraksi']).execute()
                facility = facility_result.data[0] if facility_result.data else {}
                
                # Create reservation
                reservasi_data = {
                    'username_p': request.session.get('username'),
                    'nama_atraksi': cd['nama_atraksi'],
                    'tanggal_kunjungan': cd['tanggal_kunjungan'].isoformat(),
                    'jumlah_tiket': cd['jumlah_tiket'],
                    'status': 'Terjadwal'
                }
                
                result = supabase.table('reservasi').insert(reservasi_data).execute()
                
                if result.data:
                    messages.success(request, f"Reservasi untuk {cd['nama_atraksi']} berhasil dibuat.")
                    return redirect('tickets:detail_reservasi', 
                                  username_p=request.session.get('username'),
                                  nama_atraksi=cd['nama_atraksi'], 
                                  tanggal_kunjungan=cd['tanggal_kunjungan'].isoformat())
                else:
                    messages.error(request, "Gagal membuat reservasi")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = ReservasiForm()

    # Get attractions list for the form
    try:
        atraksi_result = supabase.table('atraksi').select('*').execute()
        
        atraksi_list = []
        for atraksi in atraksi_result.data:
            # Get facility details 
            facility_result = supabase.table('fasilitas').select('*').eq('nama', atraksi['nama_atraksi']).execute()
            facility = facility_result.data[0] if facility_result.data else {}
            
            # Get animals participating
            hewan_result = supabase.table('berpartisipasi').select('''
                hewan!inner(
                    nama,
                    spesies
                )
            ''').eq('nama_fasilitas', atraksi['nama_atraksi']).execute()
            
            # Get trainer assigned
            pelatih_result = supabase.table('jadwal_penugasan').select('''
                pelatih_hewan!inner(
                    pengguna!inner(
                        nama_depan,
                        nama_belakang
                    )
                )
            ''').eq('nama_atraksi', atraksi['nama_atraksi']).execute()
            
            hewan_list = [h['hewan']['nama'] or h['hewan']['spesies'] for h in hewan_result.data] if hewan_result.data else []
            pelatih_name = "Tidak ada"
            if pelatih_result.data:
                pengguna = pelatih_result.data[0]['pelatih_hewan']['pengguna']
                pelatih_name = f"{pengguna['nama_depan']} {pengguna['nama_belakang']}"
            
            # Format jadwal
            jadwal_formatted = "Tidak ada"
            if facility.get('jadwal'):
                try:
                    jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                    jadwal_formatted = jadwal_dt.strftime('%H:%M')
                except:
                    jadwal_formatted = str(facility['jadwal'])
            
            atraksi_list.append({
                'nama': atraksi['nama_atraksi'],
                'lokasi': atraksi['lokasi'],
                'kapasitas': facility.get('kapasitas_max', 0),
                'jadwal': jadwal_formatted,
                'pelatih': pelatih_name,
                'hewan': hewan_list
            })
        
    except Exception as e:
        atraksi_list = []
        messages.error(request, f"Error loading attractions: {str(e)}")

    return render(request, 'tambah_reservasi.html', {
        'form': form,
        'atraksi_list': atraksi_list
    })

@login_required_custom
def detail_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for viewing reservation details"""
    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')
        
        reservasi = reservasi_result.data[0]
        
        # Get attraction details 
        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_atraksi).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}
        
        # Get facility details 
        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_atraksi).execute()
        facility = facility_result.data[0] if facility_result.data else {}
        
        # Format jadwal
        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
        reservasi['jam'] = jam
        
        return render(request, 'detail_reservasi.html', {
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required_custom
def edit_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for editing a reservation"""
    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')
        
        reservasi = reservasi_result.data[0]
        
        if request.method == 'POST':
            if 'jumlah_tiket' in request.POST:
                try:
                    new_jumlah = int(request.POST.get('jumlah_tiket'))
                    
                    update_result = supabase.table('reservasi').update({
                        'jumlah_tiket': new_jumlah
                    }).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                    
                    if update_result.data:
                        messages.success(request, "Reservasi berhasil diubah")
                        return redirect('tickets:detail_reservasi', 
                                      username_p=username_p,
                                      nama_atraksi=nama_atraksi, 
                                      tanggal_kunjungan=tanggal_kunjungan)
                    else:
                        messages.error(request, "Gagal mengubah reservasi")
                except Exception as e:
                    messages.error(request, f"Error updating reservation: {str(e)}")
        
        # Get attraction and facility details
        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_atraksi).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}
        
        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_atraksi).execute()
        facility = facility_result.data[0] if facility_result.data else {}
        
        # Format jadwal
        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
        reservasi['jam'] = jam
        
        form = ReservasiEditForm(initial={
            'jumlah_tiket': reservasi['jumlah_tiket'],
            'status': reservasi['status']
        })
        
        return render(request, 'edit_reservasi.html', {
            'form': form,
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required_custom
def batalkan_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for cancelling a reservation"""
    try:
        current_username = request.session.get('username')
        
        # Check if reservation exists and belongs to user
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        
        if not reservasi_result.data:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')
            
        # Cek ownership
        if reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Anda tidak memiliki akses ke reservasi ini")
            return redirect('tickets:tambah_reservasi')

        if request.method == 'POST':
            # Update dengan error handling yang lebih detail
            try:
                update_result = supabase.table('reservasi').update({
                    'status': 'Dibatalkan'
                }).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
                
                # Cek apakah ada error dari Supabase
                if hasattr(update_result, 'error') and update_result.error:
                    messages.error(request, f"Error dari database: {update_result.error}")
                    return redirect('tickets:tambah_reservasi')
                
                # Verifikasi update berhasil dengan query ulang
                verify_result = supabase.table('reservasi').select('status').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
                if verify_result.data and verify_result.data[0]['status'] == 'Dibatalkan':
                    messages.success(request, "Reservasi berhasil dibatalkan")
                else:
                    messages.error(request, "Update tidak berhasil - status tidak berubah")
                    
            except Exception as update_error:
                messages.error(request, f"Error saat update: {str(update_error)}")
                
            return redirect('tickets:tambah_reservasi')
            
        return redirect('tickets:detail_reservasi', 
                       username_p=username_p, 
                       nama_atraksi=nama_atraksi, 
                       tanggal_kunjungan=tanggal_kunjungan)
                       
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

# Admin views
@login_required_custom
def admin_list_reservasi(request):
    """Admin view for listing all reservations"""
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)
    request.session['user_role'] = user_role
    
    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')
    
    try:
        # Get all reservations
        reservasi_result = supabase.table('reservasi').select('*').execute()
        
        reservasi_list = []
        for reservasi in reservasi_result.data:
            # Get user details
            user_result = supabase.table('pengguna').select('*').eq('username', reservasi['username_p']).execute()
            user = user_result.data[0] if user_result.data else {}
            
            # Get attraction details
            atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', reservasi['nama_atraksi']).execute()
            atraksi = atraksi_result.data[0] if atraksi_result.data else {}
            
            # Get facility details
            facility_result = supabase.table('fasilitas').select('*').eq('nama', reservasi['nama_atraksi']).execute()
            facility = facility_result.data[0] if facility_result.data else {}
            
            # Format jadwal
            jam = "Tidak ada"
            if facility.get('jadwal'):
                try:
                    jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                    jam = jadwal_dt.strftime('%H:%M')
                except:
                    jam = str(facility['jadwal'])
            
            # Add formatted data
            reservasi['nama_lengkap'] = f"{user.get('nama_depan', '')} {user.get('nama_belakang', '')}"
            reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
            reservasi['jam'] = jam
            
            reservasi_list.append(reservasi)
        
        # Sort by tanggal_kunjungan descending
        reservasi_list.sort(key=lambda x: x['tanggal_kunjungan'], reverse=True)
        
        return render(request, 'admin_list_reservasi.html', {
            'reservasi_list': reservasi_list
        })
    except Exception as e:
        messages.error(request, f"Error loading reservations: {str(e)}")
        return render(request, 'admin_list_reservasi.html', {
            'reservasi_list': []
        })

@login_required_custom
def admin_edit_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """Admin view for editing any reservation"""
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)
    
    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')

    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
        if not reservasi_result.data:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:admin_list_reservasi')
        
        reservasi = reservasi_result.data[0]
        
        if request.method == 'POST':
            update_data = {}
            
            if 'jumlah_tiket' in request.POST:
                jumlah_tiket = request.POST.get('jumlah_tiket')
                if jumlah_tiket:
                    update_data['jumlah_tiket'] = int(jumlah_tiket)
            
            if 'status' in request.POST:
                status = request.POST.get('status')
                if status:
                    update_data['status'] = status
                        
            if update_data:
                try:
                    # Update dengan error handling yang lebih detail
                    update_result = supabase.table('reservasi').update(update_data).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                                        
                    # Cek error dari Supabase
                    if hasattr(update_result, 'error') and update_result.error:
                        messages.error(request, f"Error dari database: {update_result.error}")
                        return redirect('tickets:admin_list_reservasi')
                    
                    # Verifikasi update dengan query ulang
                    verify_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                    
                    if verify_result.data:
                        updated_reservasi = verify_result.data[0]
                        
                        # Cek apakah data benar-benar berubah
                        update_success = True
                        if 'status' in update_data and updated_reservasi['status'] != update_data['status']:
                            update_success = False
                        if 'jumlah_tiket' in update_data and updated_reservasi['jumlah_tiket'] != update_data['jumlah_tiket']:
                            update_success = False
                            
                        if update_success:
                            messages.success(request, "Reservasi berhasil diubah")
                        else:
                            messages.error(request, "Update tidak berhasil - data tidak berubah")
                    else:
                        messages.error(request, "Gagal memverifikasi update")
                        
                except Exception as update_error:
                    messages.error(request, f"Error saat update: {str(update_error)}")
            
            return redirect('tickets:admin_list_reservasi')
        
        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_atraksi).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}
        
        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_atraksi).execute()
        facility = facility_result.data[0] if facility_result.data else {}
        
        # Format jadwal
        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
        reservasi['jam'] = jam
        
        form = AdminReservasiEditForm(initial={
            'username_p': reservasi['username_p'],
            'nama_atraksi': reservasi['nama_atraksi'],
            'tanggal_kunjungan': reservasi['tanggal_kunjungan'],
            'jumlah_tiket': reservasi['jumlah_tiket'],
            'status': reservasi['status']
        })
        
        return render(request, 'admin_edit_reservasi.html', {
            'form': form,
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:admin_list_reservasi')


@login_required_custom
def admin_batalkan_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """Admin view for cancelling a reservation from the list (via modal)"""
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)
    
    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')
    
    try:       
        # Check if reservation exists
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
        if not reservasi_result.data:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:admin_list_reservasi')
        
        if request.method == 'POST' and 'confirm' in request.POST:
            try:
                update_result = supabase.table('reservasi').update({
                    'status': 'Dibatalkan'
                }).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                                
                # Cek error dari Supabase
                if hasattr(update_result, 'error') and update_result.error:
                    messages.error(request, f"Error dari database: {update_result.error}")
                    return redirect('tickets:admin_list_reservasi')
                
                # Verifikasi update berhasil
                verify_result = supabase.table('reservasi').select('status').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
                if verify_result.data and verify_result.data[0]['status'] == 'Dibatalkan':
                    messages.success(request, "Reservasi berhasil dibatalkan")
                else:
                    messages.error(request, "Update tidak berhasil - status tidak berubah")
                    
            except Exception as update_error:
                messages.error(request, f"Error saat update: {str(update_error)}")
        
        return redirect('tickets:admin_list_reservasi')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:admin_list_reservasi')

@login_required_custom
def user_reservasi_list(request):
    """View to list user's reservations"""
    try:
        current_username = request.session.get('username')
        
        # Get user's reservations
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', current_username).execute()
        
        reservasi_list = []
        for reservasi in reservasi_result.data:
            # Get attraction details
            atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', reservasi['nama_atraksi']).execute()
            atraksi = atraksi_result.data[0] if atraksi_result.data else {}
            
            # Get facility details
            facility_result = supabase.table('fasilitas').select('*').eq('nama', reservasi['nama_atraksi']).execute()
            facility = facility_result.data[0] if facility_result.data else {}
            
            # Format jadwal
            jam = "Tidak ada"
            if facility.get('jadwal'):
                try:
                    jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                    jam = jadwal_dt.strftime('%H:%M')
                except:
                    jam = str(facility['jadwal'])
            
            # Add formatted data
            reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
            reservasi['jam'] = jam
            
            reservasi_list.append(reservasi)
        
        # Sort by tanggal_kunjungan descending
        reservasi_list.sort(key=lambda x: x['tanggal_kunjungan'], reverse=True)
        
        return render(request, 'user_reservasi_list.html', {
            'reservasi_list': reservasi_list
        })
    except Exception as e:
        messages.error(request, f"Error loading reservations: {str(e)}")
        return render(request, 'user_reservasi_list.html', {
            'reservasi_list': []
        })