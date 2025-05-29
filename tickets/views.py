# views tickets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ReservasiForm, ReservasiEditForm, AdminReservasiEditForm, ReservasiWahanaEditForm, ReservasiWahanaForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
from supabase_client import supabase
from main.views import login_required_custom, get_user_role
from datetime import date, timedelta
import uuid
from datetime import datetime

@login_required_custom
def list_reservasi(request):
    try:
        current_username = request.session.get('username')
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', current_username).execute()

        reservasi_list = []
        for reservasi in reservasi_result.data:
            nama_fasilitas = reservasi.get('nama_fasilitas') or reservasi.get('nama_atraksi') or ''

            if not nama_fasilitas:
                continue

            atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_fasilitas).execute()
            wahana_result = supabase.table('wahana').select('*').eq('nama_wahana', nama_fasilitas).execute()
            jenis_reservasi = "Atraksi" if atraksi_result.data else "Wahana"

            facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
            facility = facility_result.data[0] if facility_result.data else {}

            reservasi_data = {
                'jenis_reservasi': jenis_reservasi,
                'nama_fasilitas': nama_fasilitas,
                'tanggal_kunjungan': reservasi.get('tanggal_kunjungan'),
                'jumlah_tiket': reservasi.get('jumlah_tiket'),
                'status': reservasi.get('status'),
                'kapasitas_max': facility.get('kapasitas_max', 0),
                'username_p': reservasi.get('username_p')
            }

            reservasi_list.append(reservasi_data)

        reservasi_list.sort(key=lambda x: x['tanggal_kunjungan'], reverse=True)

        return render(request, 'list_reservasi.html', {
            'reservasi_list': reservasi_list
        })

    except Exception as e:
        messages.error(request, f"Error loading reservations: {str(e)}")
        return render(request, 'list_reservasi.html', {
            'reservasi_list': []
        })

@login_required_custom
def list_reservasi_tersedia(request):
    try:
        today = date.today()
        tanggal_ke_depan = [(today + timedelta(days=i)).isoformat() for i in range(5)]
        fasilitas_list = []
        current_user = request.session.get('username')

        user_reservasi_result = supabase.table('reservasi') \
            .select('nama_fasilitas, tanggal_kunjungan') \
            .eq('username_p', current_user) \
            .eq('status', 'Terjadwal') \
            .execute()

        user_reservasi = {
            (r['nama_fasilitas'], r['tanggal_kunjungan'])
            for r in user_reservasi_result.data
        } if user_reservasi_result.data else set()

        # ATRAKSI
        atraksi_result = supabase.table('atraksi').select('*').execute()
        for atraksi in atraksi_result.data:
            nama_fasilitas = atraksi['nama_atraksi']
            facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
            facility = facility_result.data[0] if facility_result.data else {}
            kapasitas_max = facility.get('kapasitas_max', 0)

            for tanggal in tanggal_ke_depan:
                reservasi_tanggal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', nama_fasilitas) \
                    .eq('tanggal_kunjungan', tanggal) \
                    .eq('status', 'Terjadwal') \
                    .execute()
                
                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_tanggal_result.data]) if reservasi_tanggal_result.data else 0
                kapasitas_tersedia = max(0, kapasitas_max - total_reserved)

                fasilitas_list.append({
                    'jenis_reservasi': 'Atraksi',
                    'nama_fasilitas': nama_fasilitas,
                    'tanggal_kunjungan': tanggal,
                    'kapasitas_max': kapasitas_max,
                    'kapasitas_tersedia': kapasitas_tersedia,
                    'is_user_reserved': (nama_fasilitas, tanggal) in user_reservasi,
                })

        # WAHANA
        wahana_result = supabase.table('wahana').select('*').execute()
        for wahana in wahana_result.data:
            nama_fasilitas = wahana['nama_wahana']
            facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
            facility = facility_result.data[0] if facility_result.data else {}
            kapasitas_max = facility.get('kapasitas_max', 0)

            for tanggal in tanggal_ke_depan:
                reservasi_tanggal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', nama_fasilitas) \
                    .eq('tanggal_kunjungan', tanggal) \
                    .eq('status', 'Terjadwal') \
                    .execute()
                
                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_tanggal_result.data]) if reservasi_tanggal_result.data else 0
                kapasitas_tersedia = max(0, kapasitas_max - total_reserved)

                fasilitas_list.append({
                    'jenis_reservasi': 'Wahana',
                    'nama_fasilitas': nama_fasilitas,
                    'tanggal_kunjungan': tanggal,
                    'kapasitas_max': kapasitas_max,
                    'kapasitas_tersedia': kapasitas_tersedia,
                    'is_user_reserved': (nama_fasilitas, tanggal) in user_reservasi,
                })

        return render(request, 'list_reservasi_tersedia.html', {
            'fasilitas_list': fasilitas_list
        })

    except Exception as e:
        messages.error(request, f"Error loading available facilities: {str(e)}")
        return render(request, 'list_reservasi_tersedia.html', {
            'fasilitas_list': []
        })

@login_required_custom
def tambah_reservasi(request):
    prefill_nama = None
    prefill_tanggal = None
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                attraction_result = supabase.table('atraksi').select('*').eq('nama_atraksi', cd['nama_atraksi']).execute()
                if not attraction_result.data:
                    messages.error(request, "Atraksi tidak ditemukan")
                    return redirect('tickets:tambah_reservasi')

                facility_result = supabase.table('fasilitas').select('*').eq('nama', cd['nama_atraksi']).execute()
                facility = facility_result.data[0] if facility_result.data else {}
                kapasitas_max = facility.get('kapasitas_max', 0)

                reservasi_terjadwal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', cd['nama_atraksi']) \
                    .eq('status', 'Terjadwal').execute()
                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_terjadwal_result.data]) if reservasi_terjadwal_result.data else 0
                sisa_kapasitas = kapasitas_max - total_reserved

                # to trigger the trigger
                # if cd['jumlah_tiket'] > sisa_kapasitas:
                #     messages.error(request, f"Tiket tidak mencukupi. Sisa tiket tersedia: {sisa_kapasitas}")
                #     return redirect('tickets:tambah_reservasi')

                supabase.table('reservasi') \
                    .delete() \
                    .eq('username_p', request.session.get('username')) \
                    .eq('nama_fasilitas', cd['nama_atraksi']) \
                    .eq('tanggal_kunjungan', cd['tanggal_kunjungan'].isoformat()) \
                    .eq('status', 'Dibatalkan') \
                .execute()

                reservasi_data = {
                    'username_p': request.session.get('username'),
                    'nama_fasilitas': cd['nama_atraksi'],
                    'tanggal_kunjungan': cd['tanggal_kunjungan'].isoformat(),
                    'jumlah_tiket': cd['jumlah_tiket'],
                    'status': 'Terjadwal'
                }

                result = supabase.table('reservasi').insert(reservasi_data).execute()
                if result.data:
                    messages.success(request, f"Reservasi untuk {cd['nama_atraksi']} berhasil dibuat.")
                    return redirect('tickets:detail_reservasi',
                                    username_p=request.session.get('username'),
                                    nama_fasilitas=cd['nama_atraksi'],
                                    tanggal_kunjungan=cd['tanggal_kunjungan'].isoformat())
                else:
                    messages.error(request, "Gagal membuat reservasi")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = ReservasiForm()
        prefill_nama = request.GET.get("nama")
        prefill_tanggal = request.GET.get("tanggal")

        if prefill_nama:
            form.fields['nama_atraksi'].initial = prefill_nama
        if prefill_tanggal:
            form.fields['tanggal_kunjungan'].initial = prefill_tanggal

    try:
        atraksi_result = supabase.table('atraksi').select('*').execute()
        atraksi_list = []
        for atraksi in atraksi_result.data:
            facility_result = supabase.table('fasilitas').select('*').eq('nama', atraksi['nama_atraksi']).execute()
            facility = facility_result.data[0] if facility_result.data else {}

            hewan_result = supabase.table('berpartisipasi').select('hewan!inner(nama,spesies)').eq('nama_fasilitas', atraksi['nama_atraksi']).execute()
            pelatih_result = supabase.table('jadwal_penugasan').select('pelatih_hewan!inner(pengguna!inner(nama_depan,nama_belakang))').eq('nama_atraksi', atraksi['nama_atraksi']).execute()
            hewan_list = [h['hewan']['nama'] or h['hewan']['spesies'] for h in hewan_result.data] if hewan_result.data else []

            pelatih_name = "Tidak ada"
            if pelatih_result.data:
                pengguna = pelatih_result.data[0]['pelatih_hewan']['pengguna']
                pelatih_name = f"{pengguna['nama_depan']} {pengguna['nama_belakang']}"

            jadwal_formatted = "Tidak ada"
            if facility.get('jadwal'):
                try:
                    jadwal_formatted = facility['jadwal'][:5]
                except:
                    jadwal_formatted = str(facility['jadwal'])

            atraksi_list.append({
                'nama': atraksi['nama_atraksi'],
                'lokasi': atraksi['lokasi'],
                'kapasitas': facility.get('kapasitas_max', 0),
                'jadwal': jadwal_formatted,
                'pelatih': pelatih_name,
                'hewan': hewan_list,
            })
    except Exception as e:
        atraksi_list = []
        messages.error(request, f"Error loading attractions: {str(e)}")

    today = date.today()
    return render(request, 'tambah_reservasi.html', {
        'form': form,
        'atraksi_list': atraksi_list,
        'prefill_nama': prefill_nama,
        'prefill_tanggal': prefill_tanggal,
        'today_date': today.isoformat(),
    })

@login_required_custom
def detail_reservasi(request, username_p, nama_fasilitas, tanggal_kunjungan):
    """View for viewing reservation details"""
    try:
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')

        reservasi = reservasi_result.data[0]

        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_fasilitas).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}

        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
        facility = facility_result.data[0] if facility_result.data else {}

        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])

        reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
        reservasi['jam'] = jam
        reservasi['nama_atraksi'] = nama_fasilitas  # For template compatibility

        return render(request, 'detail_reservasi.html', {
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required_custom
def edit_reservasi(request, username_p, nama_fasilitas, tanggal_kunjungan):
    try:
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi')

        reservasi = reservasi_result.data[0]

        if request.method == 'POST' and 'jumlah_tiket' in request.POST:
            try:
                new_jumlah = int(request.POST.get('jumlah_tiket'))
                old_jumlah = reservasi['jumlah_tiket']

                facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
                facility = facility_result.data[0] if facility_result.data else {}
                kapasitas_max = facility.get('kapasitas_max', 0)

                reservasi_terjadwal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', nama_fasilitas) \
                    .eq('tanggal_kunjungan', tanggal_kunjungan) \
                    .eq('status', 'Terjadwal') \
                    .neq('username_p', username_p) \
                    .execute()

                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_terjadwal_result.data]) if reservasi_terjadwal_result.data else 0
                sisa_kapasitas = kapasitas_max - total_reserved

                # untuk mentrigger trigger
                # if new_jumlah > sisa_kapasitas + old_jumlah:
                #     messages.error(request, f"Tiket tidak mencukupi. Sisa tiket tersedia: {sisa_kapasitas + old_jumlah - total_reserved}")
                #     return redirect('tickets:edit_reservasi', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)

                supabase.table('reservasi').update({'jumlah_tiket': new_jumlah}).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

                messages.success(request, "Reservasi berhasil diubah")
                return redirect('tickets:detail_reservasi', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)
            except Exception as e:
                messages.error(request, f"Error updating reservation: {str(e)}")

        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_fasilitas
).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}

        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
        facility = facility_result.data[0] if facility_result.data else {}

        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])

            reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
            reservasi['jam'] = jam

        form = ReservasiEditForm(initial={
            'jumlah_tiket': reservasi['jumlah_tiket'],
            'status': reservasi['status']
        })

        reservasi['nama_fasilitas'] = reservasi.get('nama_fasilitas') or nama_fasilitas
        return render(request, 'edit_reservasi.html', {
            'form': form,
            'reservasi': reservasi
        })

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required_custom
def batalkan_reservasi(request, username_p, nama_fasilitas, tanggal_kunjungan):
    try:
        current_username = request.session.get('username')
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan atau Anda tidak memiliki akses")
            return redirect('tickets:tambah_reservasi')

        if request.method == 'POST':
            try:
                supabase.table('reservasi').update({'status': 'Dibatalkan'}).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                messages.success(request, "Reservasi berhasil dibatalkan")
            except Exception as e:
                messages.error(request, f"Error saat membatalkan: {str(e)}")

            return redirect('tickets:list_reservasi')

        return redirect('tickets:detail_reservasi', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi')

@login_required_custom
def tambah_reservasi_wahana(request):
    prefill_nama = request.GET.get("nama")
    prefill_tanggal = request.GET.get("tanggal")

    if request.method == 'POST':
        form = ReservasiWahanaForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                wahana_result = supabase.table('wahana').select('*').eq('nama_wahana', cd['nama_wahana']).execute()
                if not wahana_result.data:
                    messages.error(request, "Wahana tidak ditemukan")
                    return redirect('tickets:tambah_reservasi_wahana')

                facility_result = supabase.table('fasilitas').select('*').eq('nama', cd['nama_wahana']).execute()
                facility = facility_result.data[0] if facility_result.data else {}
                kapasitas_max = facility.get('kapasitas_max', 0)

                reservasi_terjadwal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', cd['nama_wahana']) \
                    .eq('tanggal_kunjungan', cd['tanggal_kunjungan'].isoformat()) \
                    .eq('status', 'Terjadwal').execute()
                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_terjadwal_result.data]) if reservasi_terjadwal_result.data else 0
                sisa_kapasitas = kapasitas_max - total_reserved

                # Validasi kapasitas di sisi frontend
                if cd['jumlah_tiket'] > sisa_kapasitas:
                    messages.error(request, f"Tiket tidak mencukupi. Sisa tiket tersedia: {sisa_kapasitas}")
                    return redirect('tickets:tambah_reservasi_wahana')
                
                supabase.table('reservasi') \
                    .delete() \
                    .eq('username_p', request.session.get('username')) \
                    .eq('nama_fasilitas', cd['nama_wahana']) \
                    .eq('tanggal_kunjungan', cd['tanggal_kunjungan'].isoformat()) \
                    .eq('status', 'Dibatalkan') \
                    .execute()

                reservasi_data = {
                    'username_p': request.session.get('username'),
                    'nama_fasilitas': cd['nama_wahana'],
                    'tanggal_kunjungan': cd['tanggal_kunjungan'].isoformat(),
                    'jumlah_tiket': cd['jumlah_tiket'],
                    'status': 'Terjadwal'
                }

                result = supabase.table('reservasi').insert(reservasi_data).execute()
                if result.data:
                    messages.success(request, f"Reservasi untuk {cd['nama_wahana']} berhasil dibuat.")
                    return redirect('tickets:detail_reservasi_wahana',
                                    username_p=request.session.get('username'),
                                    nama_fasilitas=cd['nama_wahana'],
                                    tanggal_kunjungan=cd['tanggal_kunjungan'].isoformat())
                else:
                    messages.error(request, "Gagal membuat reservasi")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = ReservasiWahanaForm()
        if prefill_nama:
            form.fields['nama_wahana'].initial = prefill_nama
        if prefill_tanggal:
            form.fields['tanggal_kunjungan'].initial = prefill_tanggal

    # Tetap ambil daftar wahana
    try:
        wahana_result = supabase.table('wahana').select('*').execute()
        wahana_list = []
        for wahana in wahana_result.data:
            facility_result = supabase.table('fasilitas').select('*').eq('nama', wahana['nama_wahana']).execute()
            facility = facility_result.data[0] if facility_result.data else {}

            jadwal_formatted = "Tidak ada"
            if facility.get('jadwal'):
                try:
                    jadwal_formatted = facility['jadwal'][:5]
                except:
                    jadwal_formatted = str(facility['jadwal'])

            peraturan_list = []
            if wahana.get('peraturan'):
                peraturan_raw = wahana['peraturan'].replace('\n', '. ').replace(';', '. ')
                peraturan_list = [p.strip() for p in peraturan_raw.split('.') if p.strip()]

            wahana_list.append({
                'nama': wahana['nama_wahana'],
                'peraturan': peraturan_list,
                'kapasitas': facility.get('kapasitas_max', 0),
                'jadwal': jadwal_formatted,
            })
    except Exception as e:
        wahana_list = []
        messages.error(request, f"Error loading wahana: {str(e)}")

    today = date.today()
    return render(request, 'tambah_reservasi_wahana.html', {
        'form': form,
        'wahana_list': wahana_list,
        'prefill_nama': prefill_nama,
        'prefill_tanggal': prefill_tanggal,
        'today_date': today.isoformat(),
    })

@login_required_custom
def detail_reservasi_wahana(request, username_p, nama_fasilitas, tanggal_kunjungan):
    """View for viewing wahana reservation details"""
    try:
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi_wahana')

        reservasi = reservasi_result.data[0]

        wahana_result = supabase.table('wahana').select('*').eq('nama_wahana', nama_fasilitas).execute()
        wahana = wahana_result.data[0] if wahana_result.data else {}

        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
        facility = facility_result.data[0] if facility_result.data else {}

        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])

        peraturan_list = []
        if wahana.get('peraturan'):
            peraturan_raw = wahana['peraturan'].replace('\n', '. ').replace(';', '. ')
            peraturan_list = [p.strip() for p in peraturan_raw.split('.') if p.strip()]

        reservasi['peraturan'] = peraturan_list
        reservasi['jam'] = jam
        reservasi['nama_wahana'] = nama_fasilitas  # For template compatibility

        return render(request, 'detail_reservasi_wahana.html', {
            'reservasi': reservasi
        })
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi_wahana')

@login_required_custom
def edit_reservasi_wahana(request, username_p, nama_fasilitas, tanggal_kunjungan):
    try:
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
        current_username = request.session.get('username')
        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:tambah_reservasi_wahana')

        reservasi = reservasi_result.data[0]

        if request.method == 'POST' and 'jumlah_tiket' in request.POST:
            try:
                new_jumlah = int(request.POST.get('jumlah_tiket'))
                old_jumlah = reservasi['jumlah_tiket']

                facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
                facility = facility_result.data[0] if facility_result.data else {}
                kapasitas_max = facility.get('kapasitas_max', 0)

                reservasi_terjadwal_result = supabase.table('reservasi') \
                    .select('jumlah_tiket') \
                    .eq('nama_fasilitas', nama_fasilitas) \
                    .eq('tanggal_kunjungan', tanggal_kunjungan) \
                    .eq('status', 'Terjadwal') \
                    .neq('username_p', username_p) \
                    .execute()

                total_reserved = sum([r['jumlah_tiket'] for r in reservasi_terjadwal_result.data]) if reservasi_terjadwal_result.data else 0
                sisa_kapasitas = kapasitas_max - total_reserved

                # untuk mentrigger trigger
                # if new_jumlah > sisa_kapasitas + old_jumlah:
                #     messages.error(request, f"Tiket tidak mencukupi. Sisa tiket tersedia: {sisa_kapasitas + old_jumlah - total_reserved}")
                #     return redirect('tickets:edit_reservasi_wahana', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)

                supabase.table('reservasi').update({'jumlah_tiket': new_jumlah}).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

                messages.success(request, "Reservasi berhasil diubah")
                return redirect('tickets:detail_reservasi_wahana', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)
            except Exception as e:
                messages.error(request, f"Error updating reservation: {str(e)}")

        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
        facility = facility_result.data[0] if facility_result.data else {}

        jam = "Tidak ada"
        if facility.get('jadwal'):
            try:
                jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                jam = jadwal_dt.strftime('%H:%M')
            except:
                jam = str(facility['jadwal'])
            reservasi['jam'] = jam

        form = ReservasiWahanaEditForm(initial={
            'username_p': username_p,
            'nama_fasilitas': nama_fasilitas,
            'tanggal_kunjungan': tanggal_kunjungan,
            'jumlah_tiket': reservasi['jumlah_tiket'],
            'status': reservasi['status']
        })

        return render(request, 'edit_reservasi_wahana.html', {
            'form': form,
            'reservasi': reservasi
        })

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi_wahana')

@login_required_custom
def batalkan_reservasi_wahana(request, username_p, nama_fasilitas, tanggal_kunjungan):
    try:
        current_username = request.session.get('username')
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

        if not reservasi_result.data or reservasi_result.data[0]['username_p'] != current_username:
            messages.error(request, "Reservasi tidak ditemukan atau Anda tidak memiliki akses")
            return redirect('tickets:tambah_reservasi_wahana')

        if request.method == 'POST':
            try:
                supabase.table('reservasi').update({'status': 'Dibatalkan'}).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()
                messages.success(request, "Reservasi berhasil dibatalkan")
            except Exception as e:
                messages.error(request, f"Error saat membatalkan: {str(e)}")

            return redirect('tickets:list_reservasi')

        return redirect('tickets:detail_reservasi_wahana', username_p=username_p, nama_fasilitas=nama_fasilitas, tanggal_kunjungan=tanggal_kunjungan)

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('tickets:tambah_reservasi_wahana')
    
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
            nama_fasilitas_reservasi = reservasi.get('nama_atraksi') or reservasi.get('nama_fasilitas')
            if not nama_fasilitas_reservasi:
                continue

            # Get user details
            user_result = supabase.table('pengguna').select('*').eq('username', reservasi['username_p']).execute()
            user = user_result.data[0] if user_result.data else {}

            atraksi = {}
            facility = {}
            jam = "Tidak ada"
            jenis_reservasi = "Tidak diketahui"

            atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_fasilitas_reservasi).execute()
            if atraksi_result.data:
                jenis_reservasi = 'Atraksi'
                atraksi = atraksi_result.data[0]
                facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas_reservasi).execute()
                facility = facility_result.data[0] if facility_result.data else {}

                if facility.get('jadwal'):
                    try:
                        jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                        jam = jadwal_dt.strftime('%H:%M')
                    except:
                        jam = str(facility['jadwal'])

            else:
                wahana_result = supabase.table('wahana').select('*').eq('nama_wahana', nama_fasilitas_reservasi).execute()
                if wahana_result.data:
                    jenis_reservasi = 'Wahana'
                    facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas_reservasi).execute()
                    facility = facility_result.data[0] if facility_result.data else {}

                    if facility.get('jadwal'):
                        try:
                            jadwal_dt = datetime.fromisoformat(facility['jadwal'].replace('Z', '+00:00'))
                            jam = jadwal_dt.strftime('%H:%M')
                        except:
                            jam = str(facility['jadwal'])

            reservasi['nama_lengkap'] = f"{user.get('nama_depan', '')} {user.get('nama_belakang', '')}"
            reservasi['lokasi'] = atraksi.get('lokasi', 'Tidak ada')
            reservasi['jam'] = jam
            reservasi['jenis_reservasi'] = jenis_reservasi

            reservasi_list.append(reservasi)

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
def admin_edit_reservasi(request, username_p, nama_fasilitas, tanggal_kunjungan):
    """Admin view for editing any reservation"""
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')

    try:
        # Get reservation
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

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
                    update_result = supabase.table('reservasi').update(update_data).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

                    # Cek error dari Supabase
                    if hasattr(update_result, 'error') and update_result.error:
                        messages.error(request, f"Error dari database: {update_result.error}")
                        return redirect('tickets:admin_list_reservasi')

                    # Verifikasi update dengan query ulang
                    verify_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

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

        atraksi_result = supabase.table('atraksi').select('*').eq('nama_atraksi', nama_fasilitas).execute()
        atraksi = atraksi_result.data[0] if atraksi_result.data else {}

        facility_result = supabase.table('fasilitas').select('*').eq('nama', nama_fasilitas).execute()
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
            'nama_atraksi': reservasi.get('nama_atraksi') or reservasi.get('nama_fasilitas'),
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
def admin_batalkan_reservasi(request, username_p, nama_fasilitas, tanggal_kunjungan):
    """Admin view for cancelling a reservation from the list (via modal)"""
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('tickets:tambah_reservasi')

    try:
        # Check if reservation exists
        reservasi_result = supabase.table('reservasi').select('*').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

        if not reservasi_result.data:
            messages.error(request, "Reservasi tidak ditemukan")
            return redirect('tickets:admin_list_reservasi')

        if request.method == 'POST' and 'confirm' in request.POST:
            try:
                update_result = supabase.table('reservasi').update({
                    'status': 'Dibatalkan'
                }).eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

                # Cek error dari Supabase
                if hasattr(update_result, 'error') and update_result.error:
                    messages.error(request, f"Error dari database: {update_result.error}")
                    return redirect('tickets:admin_list_reservasi')

                # Verifikasi update berhasil
                verify_result = supabase.table('reservasi').select('status').eq('username_p', username_p).eq('nama_fasilitas', nama_fasilitas).eq('tanggal_kunjungan', tanggal_kunjungan).execute()

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