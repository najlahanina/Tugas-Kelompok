# views tickets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReservasiForm, ReservasiEditForm, AdminReservasiEditForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
from supabase_client import supabase
import uuid
from datetime import datetime

def get_user_role(username):
    """Get user role from database"""
    try:
        # Check pengunjung
        pengunjung = supabase.table('pengunjung').select('username_p').eq('username_p', username).execute()
        if pengunjung.data:
            return 'pengunjung'
        
        # Check dokter_hewan
        dokter = supabase.table('dokter_hewan').select('username_dh').eq('username_dh', username).execute()
        if dokter.data:
            return 'dokter_hewan'
        
        # Check penjaga_hewan
        penjaga = supabase.table('penjaga_hewan').select('username_jh').eq('username_jh', username).execute()
        if penjaga.data:
            return 'penjaga_hewan'
        
        # Check pelatih_hewan
        pelatih = supabase.table('pelatih_hewan').select('username_lh').eq('username_lh', username).execute()
        if pelatih.data:
            return 'pelatih_hewan'
        
        # Check staf_admin
        admin = supabase.table('staf_admin').select('username_sa').eq('username_sa', username).execute()
        if admin.data:
            return 'admin_staff'
        
        return 'pengunjung'  # default
    except Exception as e:
        print(f"Error getting user role: {e}")
        return 'pengunjung'

@login_required
def tambah_reservasi(request):
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            try:
                # Get attraction details
                attraction_result = supabase.table('atraksi').select('''
                    nama_atraksi,
                    lokasi,
                    fasilitas!inner(
                        kapasitas_max,
                        jadwal
                    )
                ''').eq('nama_atraksi', cd['nama_atraksi']).execute()
                
                if not attraction_result.data:
                    messages.error(request, "Atraksi tidak ditemukan")
                    return redirect('tickets:tambah_reservasi')
                
                attraction = attraction_result.data[0]
                
                # Create reservation
                reservasi_data = {
                    'username_p': request.user.username,
                    'nama_atraksi': cd['nama_atraksi'],
                    'tanggal_kunjungan': cd['tanggal_kunjungan'].isoformat(),
                    'jumlah_tiket': cd['jumlah_tiket'],
                    'status': 'Terjadwal'
                }
                
                result = supabase.table('reservasi').insert(reservasi_data).execute()
                
                if result.data:
                    messages.success(request, f"Reservasi untuk {cd['nama_atraksi']} berhasil dibuat.")
                    return redirect('tickets:detail_reservasi', 
                                  username_p=request.user.username,
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
        atraksi_result = supabase.table('atraksi').select('''
            nama_atraksi,
            lokasi,
            fasilitas!inner(
                kapasitas_max,
                jadwal
            )
        ''').execute()
        
        atraksi_list = []
        for atraksi in atraksi_result.data:
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
            
            hewan_list = [h['hewan']['nama'] or h['hewan']['spesies'] for h in hewan_result.data]
            pelatih_name = "Tidak ada"
            if pelatih_result.data:
                pengguna = pelatih_result.data[0]['pelatih_hewan']['pengguna']
                pelatih_name = f"{pengguna['nama_depan']} {pengguna['nama_belakang']}"
            
            # Format jadwal
            jadwal_formatted = "Tidak ada"
            if atraksi['fasilitas']['jadwal']:
                try:
                    jadwal_dt = datetime.fromisoformat(atraksi['fasilitas']['jadwal'].replace('Z', '+00:00'))
                    jadwal_formatted = jadwal_dt.strftime('%H:%M')
                except:
                    jadwal_formatted = str(atraksi['fasilitas']['jadwal'])
            
            atraksi_list.append({
                'nama': atraksi['nama_atraksi'],
                'lokasi': atraksi['lokasi'],
                'kapasitas': atraksi['fasilitas']['kapasitas_max'],
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

@login_required
def detail_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for viewing reservation details"""
    try:
        # Get reservation with attraction details
        reservasi_result = supabase.table('reservasi').select('''
            *,
            atraksi!inner(
                lokasi,
                fasilitas!inner(
                    jadwal
                )
            )
        ''').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != request.user.username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')
        
        reservasi = reservasi_result.data[0]
        
        # Format jadwal
        jam = "Tidak ada"
        if reservasi['atraksi']['fasilitas']['jadwal']:
            try:
                jadwal_dt = datetime.fromisoformat(reservasi['atraksi']['fasilitas']['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(reservasi['atraksi']['fasilitas']['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = reservasi['atraksi']['lokasi']
        reservasi['jam'] = jam
        
        return render(request, 'detail_reservasi.html', {
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required
def edit_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for editing a reservation"""
    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('''
            *,
            atraksi!inner(
                lokasi,
                fasilitas!inner(
                    jadwal
                )
            )
        ''').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != request.user.username:
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
        
        # Format jadwal
        jam = "Tidak ada"
        if reservasi['atraksi']['fasilitas']['jadwal']:
            try:
                jadwal_dt = datetime.fromisoformat(reservasi['atraksi']['fasilitas']['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(reservasi['atraksi']['fasilitas']['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = reservasi['atraksi']['lokasi']
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

@login_required
def batalkan_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """View for cancelling a reservation"""
    try:
        # Check if reservation exists and belongs to user
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != request.user.username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')
        
        if request.method == 'POST':
            update_result = supabase.table('reservasi').update({
                'status': 'Dibatalkan'
            }).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
            
            if update_result.data:
                messages.success(request, "Reservasi berhasil dibatalkan")
            else:
                messages.error(request, "Gagal membatalkan reservasi")
            
            return redirect('tickets:tambah_reservasi')
        
        return redirect('tickets:detail_reservasi', 
                       username_p=username_p,
                       nama_atraksi=nama_atraksi, 
                       tanggal_kunjungan=tanggal_kunjungan)
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

# Admin views
@login_required
def admin_list_reservasi(request):
    """Admin view for listing all reservations"""
    user_role = get_user_role(request.user.username)
    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')
    
    try:
        # Get all reservations with user and attraction details
        reservasi_result = supabase.table('reservasi').select('''
            *,
            pengguna!inner(
                nama_depan,
                nama_belakang
            ),
            atraksi!inner(
                lokasi,
                fasilitas!inner(
                    jadwal
                )
            )
        ''').execute()
        
        reservasi_list = []
        for reservasi in reservasi_result.data:
            # Format jadwal
            jam = "Tidak ada"
            if reservasi['atraksi']['fasilitas']['jadwal']:
                try:
                    jadwal_dt = datetime.fromisoformat(reservasi['atraksi']['fasilitas']['jadwal'].replace('Z', '+00:00'))
                    jam = jadwal_dt.strftime('%H:%M')
                except:
                    jam = str(reservasi['atraksi']['fasilitas']['jadwal'])
            
            # Add formatted data
            reservasi['nama_lengkap'] = f"{reservasi['pengguna']['nama_depan']} {reservasi['pengguna']['nama_belakang']}"
            reservasi['lokasi'] = reservasi['atraksi']['lokasi']
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

@login_required
def admin_edit_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """Admin view for editing any reservation"""
    user_role = get_user_role(request.user.username)
    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')

    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('''
            *,
            atraksi!inner(
                lokasi,
                fasilitas!inner(
                    jadwal
                )
            )
        ''').eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        
        if not reservasi_result.data:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:admin_list_reservasi')
        
        reservasi = reservasi_result.data[0]
        
        if request.method == 'POST':
            update_data = {}
            
            if 'jumlah_tiket' in request.POST:
                update_data['jumlah_tiket'] = int(request.POST.get('jumlah_tiket'))
            
            if 'status' in request.POST:
                update_data['status'] = request.POST.get('status')
            
            if update_data:
                update_result = supabase.table('reservasi').update(update_data).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                
                if update_result.data:
                    messages.success(request, "Reservasi berhasil diubah")
                else:
                    messages.error(request, "Gagal mengubah reservasi")
            
            return redirect('tickets:admin_list_reservasi')
        
        # Format jadwal
        jam = "Tidak ada"
        if reservasi['atraksi']['fasilitas']['jadwal']:
            try:
                jadwal_dt = datetime.fromisoformat(reservasi['atraksi']['fasilitas']['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(reservasi['atraksi']['fasilitas']['jadwal'])
        
        # Add formatted data
        reservasi['lokasi'] = reservasi['atraksi']['lokasi']
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

@login_required
def admin_batalkan_reservasi(request, username_p, nama_atraksi, tanggal_kunjungan):
    """Admin view for cancelling a reservation from the list (via modal)"""
    user_role = get_user_role(request.user.username)
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
            update_result = supabase.table('reservasi').update({
                'status': 'Dibatalkan'
            }).eq('username_p', username_p).eq('nama_atraksi', nama_atraksi).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
            
            if update_result.data:
                messages.success(request, "Reservasi berhasil dibatalkan")
            else:
                messages.error(request, "Gagal membatalkan reservasi")
        
        return redirect('tickets:admin_list_reservasi')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:admin_list_reservasi')

@login_required
def user_reservasi_list(request):
    """View to list user's reservations"""
    try:
        # Get user's reservations
        reservasi_result = supabase.table('reservasi').select('''
            *,
            atraksi!inner(
                lokasi,
                fasilitas!inner(
                    jadwal
                )
            )
        ''').eq('username_p', request.user.username).execute()
        
        reservasi_list = []
        for reservasi in reservasi_result.data:
            # Format jadwal
            jam = "Tidak ada"
            if reservasi['atraksi']['fasilitas']['jadwal']:
                try:
                    jadwal_dt = datetime.fromisoformat(reservasi['atraksi']['fasilitas']['jadwal'].replace('Z', '+00:00'))
                    jam = jadwal_dt.strftime('%H:%M')
                except:
                    jam = str(reservasi['atraksi']['fasilitas']['jadwal'])
            
            # Add formatted data
            reservasi['lokasi'] = reservasi['atraksi']['lokasi']
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