from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservasi
from .forms import ReservasiForm, ReservasiEditForm, AdminReservasiEditForm
from attractions.models import Atraksi, Fasilitas
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count

DATA_RESERVASI = [
    {
        'id': 1,
        'username': 'arif',
        'nama_atraksi': 'Pertunjukan lumba-lumba',
        'lokasi': 'Area Akuatik',
        'jam': '10:00',
        'tanggal_kunjungan': '12-05-2025',
        'jumlah_tiket': 10,
        'status': 'Terjadwal'
    },
    {
        'id': 2,
        'username': 'winnie',
        'nama_atraksi': 'Feeding time harimau',
        'lokasi': 'Zona Harimau',
        'jam': '11:30',
        'tanggal_kunjungan': '11-05-2025',
        'jumlah_tiket': 3,
        'status': 'Terjadwal'
    },
    {
        'id': 3,
        'username': 'john',
        'nama_atraksi': 'Bird show',
        'lokasi': 'Amphitheater utama',
        'jam': '09:30',
        'tanggal_kunjungan': '13-05-2025',
        'jumlah_tiket': 5,
        'status': 'Terjadwal'
    }
]

@login_required
def tambah_reservasi(request):
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_id = max([r['id'] for r in DATA_RESERVASI]) + 1 if DATA_RESERVASI else 1

            # Cari atraksi dari DATA_ATRAKSI
            attraction = next((a for a in DATA_ATRAKSI if a['nama'] == cd['nama_atraksi']), None)
            if not attraction:
                attraction = DATA_ATRAKSI[0]  

            DATA_RESERVASI.append({
                'id': new_id,
                'username': request.user.username,
                'nama_atraksi': attraction['nama'],
                'lokasi': attraction['lokasi'],
                'jam': attraction['jadwal'],
                'tanggal_kunjungan': cd['tanggal_kunjungan'],
                'jumlah_tiket': cd['jumlah_tiket'],
                'status': 'Terjadwal'
            })

            messages.success(request, f"Reservasi untuk {attraction['nama']} berhasil dibuat.")
            return redirect('tickets:detail_reservasi', reservasi_id=new_id)
    else:
        form = ReservasiForm()

    return render(request, 'tambah_reservasi.html', {
        'form': form,
        'atraksi_list': DATA_ATRAKSI
    })


@login_required
def detail_reservasi(request, reservasi_id):
    """View for viewing reservation details"""
    reservasi = next((r for r in DATA_RESERVASI if r['id'] == reservasi_id), None)
    if not reservasi or reservasi['username'] != request.user.username:
        messages.error(request, "Reservasi tidak ditemukan")
        return redirect('tickets:tambah_reservasi')
    
    return render(request, 'detail_reservasi.html', {
        'reservasi': reservasi
    })

@login_required
def edit_reservasi(request, reservasi_id):
    """View for editing a reservation"""
    reservasi = next((r for r in DATA_RESERVASI if r['id'] == reservasi_id), None)
    if not reservasi or reservasi['username'] != request.user.username:
        messages.error(request, "Reservasi tidak ditemukan")
        return redirect('tickets:tambah_reservasi')
    
    if request.method == 'POST':
        if 'jumlah_tiket' in request.POST:
            reservasi['jumlah_tiket'] = int(request.POST.get('jumlah_tiket'))
            messages.success(request, "Reservasi berhasil diubah")
            return redirect('tickets:detail_reservasi', reservasi_id=reservasi_id)
    
    form = ReservasiEditForm(initial={
        'jumlah_tiket': reservasi['jumlah_tiket'],
        'status': reservasi['status']
    })
    
    return render(request, 'edit_reservasi.html', {
        'form': form,
        'reservasi': reservasi
    })

@login_required
def batalkan_reservasi(request, reservasi_id):
    """View for cancelling a reservation"""
    reservasi = next((r for r in DATA_RESERVASI if r['id'] == reservasi_id), None)
    if not reservasi or reservasi['username'] != request.user.username:
        messages.error(request, "Reservasi tidak ditemukan")
        return redirect('tickets:tambah_reservasi')
    
    if request.method == 'POST':
        reservasi['status'] = 'Dibatalkan'
        messages.success(request, "Reservasi berhasil dibatalkan")
        return redirect('tickets:tambah_reservasi')
    
    return redirect('tickets:detail_reservasi', reservasi_id=reservasi_id)


# Admin views
@login_required
def admin_list_reservasi(request):
    """Admin view for listing all reservations"""
    # Check if user is admin
    if not request.user.profile.role == 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')
    reservasi_list = DATA_RESERVASI
    
    return render(request, 'admin_list_reservasi.html', {
        'reservasi_list': reservasi_list
    })

@login_required
def admin_edit_reservasi(request, reservasi_id):
    """Admin view for editing any reservation"""
    # Check if user is admin
    if not request.user.profile.role == 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')

    reservasi = next((r for r in DATA_RESERVASI if r['id'] == reservasi_id), None)
    if not reservasi:
        messages.error(request, "Reservasi tidak ditemukan")
        return redirect('tickets:admin_list_reservasi')
    
    if request.method == 'POST':
        if 'jumlah_tiket' in request.POST:
            reservasi['jumlah_tiket'] = int(request.POST.get('jumlah_tiket'))
        if 'status' in request.POST:
            reservasi['status'] = request.POST.get('status')
        messages.success(request, "Reservasi berhasil diubah")
        return redirect('tickets:admin_list_reservasi')
    
    # Initialize form for rendering
    form = AdminReservasiEditForm(initial={
        'username_p': reservasi['username'],
        'nama_atraksi': reservasi['nama_atraksi'],
        'tanggal_kunjungan': reservasi['tanggal_kunjungan'],
        'jumlah_tiket': reservasi['jumlah_tiket'],
        'status': reservasi['status']
    })
    
    return render(request, 'admin_edit_reservasi.html', {
        'form': form,
        'reservasi': reservasi
    })

@login_required
def admin_batalkan_reservasi(request, reservasi_id):
    """Admin view for cancelling a reservation from the list (via modal)"""
    if not request.user.profile.role == 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')
    
    reservasi = next((r for r in DATA_RESERVASI if r['id'] == reservasi_id), None)
    if not reservasi:
        messages.error(request, "Reservasi tidak ditemukan")
        return redirect('tickets:admin_list_reservasi')
    
    if request.method == 'POST' and 'confirm' in request.POST:
        reservasi['status'] = 'Dibatalkan'
        messages.success(request, "Reservasi berhasil dibatalkan")
    
    return redirect('tickets:admin_list_reservasi')


# Dummy data for attractions (copied from the provided code)
DATA_ATRAKSI = [
    {
        'nama': 'Pertunjukan lumba-lumba',
        'lokasi': 'Area Akuatik',
        'kapasitas': 100,
        'jadwal': '10:00',
        'hewan': ['Lumba-lumba'],
        'pelatih': 'Budi'
    },
    {
        'nama': 'Feeding time harimau',
        'lokasi': 'Zona Harimau',
        'kapasitas': 75,
        'jadwal': '11:30',
        'hewan': ['Harimau'],
        'pelatih': 'Andi'
    },
    {
        'nama': 'Bird show',
        'lokasi': 'Amphitheater utama',
        'kapasitas': 150,
        'jadwal': '09:30',
        'hewan': ['Kakatua', 'Parrot'],
        'pelatih': 'Havana'
    }
]