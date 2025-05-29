#views.py attractions
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404

from main.views import get_user_role
from .forms import AtraksiForm, WahanaForm, EditAtraksiForm, EditWahanaForm
from supabase_utils import (
    get_all_atraksi, 
    get_all_wahana,
    get_wahana_by_nama,
    get_all_hewan,
    get_all_pelatih_hewan,
    get_all_fasilitas
)
from supabase_client import supabase
import uuid
from datetime import datetime

def list_atraksi(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        # Ambil data atraksi dengan join ke fasilitas untuk mendapatkan jadwal dan kapasitas
        result = supabase.table('atraksi').select('''
            nama_atraksi,
            lokasi,
            fasilitas!inner(
                jadwal,
                kapasitas_max
            )
        ''').execute()

        formatted_data = []
        for atraksi in result.data:
            jadwal_str = atraksi['fasilitas']['jadwal']
            jam_formatted = "Tidak ada"
            if jadwal_str:
                try:
                    jadwal_dt = datetime.fromisoformat(jadwal_str)
                    jam_formatted = jadwal_dt.strftime('%H:%M')
                except ValueError:
                    try:
                        time_obj = datetime.strptime(jadwal_str, '%H:%M:%S').time()
                        jam_formatted = time_obj.strftime('%H:%M')
                    except ValueError:
                        try:
                            time_obj = datetime.strptime(jadwal_str, '%H:%M').time()
                            jam_formatted = time_obj.strftime('%H:%M')
                        except ValueError:
                            jam_formatted = jadwal_str

            # Ambil hewan yang berpartisipasi dalam atraksi
            hewan_result = supabase.table('berpartisipasi').select('''
                hewan!inner(
                    nama,
                    spesies
                )
            ''').eq('nama_fasilitas', atraksi['nama_atraksi']).execute()

            # Ambil pelatih yang bertugas
            pelatih_result = supabase.table('jadwal_penugasan').select('''
                pelatih_hewan!inner(
                    pengguna!inner(
                        nama_depan,
                        nama_belakang
                    )
                )
            ''').eq('nama_atraksi', atraksi['nama_atraksi']).execute()

            hewan_list = [h['hewan']['nama'] or h['hewan']['spesies'] for h in hewan_result.data]
            pelatih_list = []
            for item in pelatih_result.data:
                pengguna = item.get('pelatih_hewan', {}).get('pengguna')
                if pengguna:
                    nama = f"{pengguna.get('nama_depan', '')} {pengguna.get('nama_belakang', '')}".strip()
                    pelatih_list.append(nama)

            formatted_data.append({
                'nama_atraksi': atraksi['nama_atraksi'],
                'nama': atraksi['nama_atraksi'],
                'lokasi': atraksi['lokasi'],
                'kapasitas': atraksi['fasilitas']['kapasitas_max'],
                'jadwal': jam_formatted,
                'hewan': hewan_list,
                'pelatih': pelatih_list
            })

        return render(request, 'atraksi_list.html', {'data_atraksi': formatted_data})
    except Exception as e:
        messages.error(request, f'Error mengambil data atraksi: {str(e)}')
        return render(request, 'atraksi_list.html', {'data_atraksi': []})

def tambah_atraksi(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    if request.method == 'POST':
        form = AtraksiForm(request.POST)
        if form.is_valid():
            try:
                nama_atraksi = form.cleaned_data['nama_atraksi']
                jadwal_atraksi = form.cleaned_data['jadwal']
                today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                pelatih_terpilih = form.cleaned_data.get('pelatih', [])
                pelatih_sudah_ditugaskan = []

                for username in pelatih_terpilih:
                    penugasan_aktif = supabase.table('jadwal_penugasan')\
                        .select('nama_atraksi')\
                        .eq('username_lh', username)\
                        .neq('nama_atraksi', nama_atraksi)\
                        .execute()

                    if penugasan_aktif.data:
                        pelatih_sudah_ditugaskan.append(username)

                if pelatih_sudah_ditugaskan:
                    usernames = ", ".join(pelatih_sudah_ditugaskan)
                    messages.error(request, f'Pelatih dengan username {usernames} sudah ditugaskan ke atraksi lain.')
                    return render(request, 'atraksi_form.html', {'form': form})
                else:
                    # 1. Insert ke tabel FASILITAS
                    fasilitas_data = {
                        'nama': nama_atraksi,
                        'jadwal': jadwal_atraksi.strftime('%Y-%m-%d %H:%M:%S'),
                        'kapasitas_max': form.cleaned_data['kapasitas_max']
                    }
                    fasilitas_result = supabase.table('fasilitas').insert(fasilitas_data).execute()
                    if fasilitas_result.data:
                        # 2. Insert ke tabel ATRAKSI
                        atraksi_data = {
                            'nama_atraksi': nama_atraksi,
                            'lokasi': form.cleaned_data['lokasi']
                        }
                        atraksi_result = supabase.table('atraksi').insert(atraksi_data).execute()
                        if atraksi_result.data:
                            # 3. Jika ada hewan yang dipilih, insert ke BERPARTISIPASI
                            if 'hewan' in form.cleaned_data and form.cleaned_data['hewan']:
                                for id_hewan in form.cleaned_data['hewan']:
                                    berpartisipasi_data = {
                                        'nama_fasilitas': nama_atraksi,
                                        'id_hewan': id_hewan
                                    }
                                    supabase.table('berpartisipasi').insert(berpartisipasi_data).execute()
                            # 4. Jika ada pelatih yang dipilih, insert ke JADWAL_PENUGASAN
                            if pelatih_terpilih:
                                for username in pelatih_terpilih:
                                    penugasan_data = {
                                        'username_lh': username,
                                        'tgl_penugasan': today,
                                        'nama_atraksi': nama_atraksi
                                    }
                                    supabase.table('jadwal_penugasan').insert(penugasan_data).execute()
                            messages.success(request, 'Atraksi berhasil ditambahkan!')
                            return redirect('attractions:list_atraksi')
                        else:
                            supabase.table('fasilitas').delete().eq('nama', nama_atraksi).execute()
                            messages.error(request, 'Gagal menambahkan atraksi.')
                    else:
                        messages.error(request, 'Gagal menambahkan fasilitas.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = AtraksiForm()
    return render(request, 'atraksi_form.html', {'form': form})

def list_wahana(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        # Ambil data wahana dengan join ke fasilitas
        result = supabase.table('wahana').select('''
            nama_wahana,
            peraturan,
            fasilitas!inner(
                jadwal,
                kapasitas_max
            )
        ''').execute()

        formatted_data = []
        for wahana in result.data:
            jadwal_str = wahana['fasilitas']['jadwal']
            jam_formatted = "Tidak ada"
            if jadwal_str:
                try:
                    jadwal_dt = datetime.fromisoformat(jadwal_str.replace('Z', '+00:00'))
                    jam_formatted = jadwal_dt.strftime('%H:%M')
                except ValueError:
                    try:
                        time_obj = datetime.strptime(jadwal_str, '%H:%M:%S').time()
                        jam_formatted = time_obj.strftime('%H:%M')
                    except ValueError:
                        try:
                            time_obj = datetime.strptime(jadwal_str, '%H:%M').time()
                            jam_formatted = time_obj.strftime('%H:%M')
                        except ValueError:
                            jam_formatted = jadwal_str

            formatted_data.append({
                'nama_wahana': wahana['nama_wahana'],
                'nama': wahana['nama_wahana'],
                'kapasitas': wahana['fasilitas']['kapasitas_max'],
                'jadwal': jam_formatted,
                'peraturan': wahana['peraturan'].split('\n') if wahana['peraturan'] else []
            })

        return render(request, 'wahana_list.html', {'data_wahana': formatted_data})
    except Exception as e:
        messages.error(request, f'Error mengambil data wahana: {str(e)}')
        return render(request, 'wahana_list.html', {'data_wahana': []})

def tambah_wahana(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    if request.method == 'POST':
        form = WahanaForm(request.POST)
        if form.is_valid():
            try:
                nama_wahana = form.cleaned_data['nama_wahana']
                
                # 1. Insert ke tabel FASILITAS terlebih dahulu
                fasilitas_data = {
                    'nama': nama_wahana,
                    'jadwal': form.cleaned_data['jadwal'].strftime('%Y-%m-%d %H:%M:%S'),
                    'kapasitas_max': form.cleaned_data['kapasitas_max']
                }
                
                fasilitas_result = supabase.table('fasilitas').insert(fasilitas_data).execute()
                
                if fasilitas_result.data:
                    # 2. Insert ke tabel WAHANA
                    wahana_data = {
                        'nama_wahana': nama_wahana,
                        'peraturan': form.cleaned_data['peraturan']
                    }
                    
                    wahana_result = supabase.table('wahana').insert(wahana_data).execute()
                    
                    if wahana_result.data:
                        messages.success(request, 'Wahana berhasil ditambahkan!')
                        return redirect('attractions:list_wahana')
                    else:
                        # Rollback fasilitas jika wahana gagal
                        supabase.table('fasilitas').delete().eq('nama', nama_wahana).execute()
                        messages.error(request, 'Gagal menambahkan wahana.')
                else:
                    messages.error(request, 'Gagal menambahkan fasilitas.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = WahanaForm()
    
    return render(request, 'wahana_form.html', {'form': form})

def edit_atraksi(request, nama_atraksi):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        atraksi_result = supabase.table('atraksi').select('''
            nama_atraksi,
            lokasi,
            fasilitas!inner(
                jadwal,
                kapasitas_max
            )
        ''').eq('nama_atraksi', nama_atraksi).execute()

        if not atraksi_result.data:
            raise Http404("Atraksi tidak ditemukan")

        atraksi = atraksi_result.data[0]

        hewan_result = supabase.table('berpartisipasi').select('''
            hewan!inner(nama, spesies)
        ''').eq('nama_fasilitas', nama_atraksi).execute()
        hewan_list = [h['hewan']['nama'] or h['hewan']['spesies'] for h in hewan_result.data]

        current_pelatih_display_result = supabase.table('jadwal_penugasan').select('''
            pelatih_hewan!inner(pengguna!inner(nama_depan, nama_belakang))
        ''').eq('nama_atraksi', nama_atraksi).execute()
        current_pelatih_display = [f"{p['pelatih_hewan']['pengguna']['nama_depan']} {p['pelatih_hewan']['pengguna']['nama_belakang']}" for p in current_pelatih_display_result.data]

        readonly_data = {
            'nama_atraksi': atraksi['nama_atraksi'],
            'lokasi': atraksi['lokasi'],
            'hewan': hewan_list,
            'pelatih': current_pelatih_display,
        }

        if request.method == 'POST':
            form = EditAtraksiForm(request.POST)
            if form.is_valid():
                try:
                    jadwal_atraksi = form.cleaned_data['jadwal']
                    pelatih_terpilih = form.cleaned_data.get('pelatih', [])
                    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    current_pelatih_result = supabase.table('jadwal_penugasan')\
                        .select('username_lh')\
                        .eq('nama_atraksi', nama_atraksi)\
                        .execute()
                    existing_usernames = [item['username_lh'] for item in current_pelatih_result.data]

                    pelatih_baru_ditambahkan = [u for u in pelatih_terpilih if u not in existing_usernames]
                    pelatih_sudah_ditugaskan = []

                    for username in pelatih_baru_ditambahkan:
                        cek = supabase.table('jadwal_penugasan')\
                            .select('nama_atraksi')\
                            .eq('username_lh', username)\
                            .neq('nama_atraksi', nama_atraksi)\
                            .execute()
                        if cek.data:
                            pelatih_sudah_ditugaskan.append(username)

                    if pelatih_sudah_ditugaskan:
                        usernames = ", ".join(pelatih_sudah_ditugaskan)
                        messages.error(request, f'Pelatih {usernames} sudah pernah ditugaskan ke atraksi lain. Tidak boleh ditambahkan.')
                        return render(request, 'atraksi_form.html', {
                            'form': form,
                            'edit_mode': True,
                            'readonly_data': readonly_data,
                        })

                    update_fasilitas_data = {
                        'kapasitas_max': form.cleaned_data['kapasitas_max'],
                        'jadwal': jadwal_atraksi.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    supabase.table('fasilitas').update(update_fasilitas_data).eq('nama', nama_atraksi).execute()

                    # 1. Update pelatih yang tetap
                    for username in pelatih_terpilih:
                        if username in existing_usernames:
                            supabase.table('jadwal_penugasan')\
                                .update({'nama_atraksi': nama_atraksi})\
                                .eq('username_lh', username)\
                                .eq('nama_atraksi', nama_atraksi)\
                                .execute()

                    # 2. Tambah pelatih baru
                    for username in pelatih_baru_ditambahkan:
                        supabase.table('jadwal_penugasan').insert({
                            'username_lh': username,
                            'tgl_penugasan': today,
                            'nama_atraksi': nama_atraksi
                        }).execute()

                    # 3. Hapus pelatih yang dihapus dari list
                    for username in existing_usernames:
                        if username not in pelatih_terpilih:
                            supabase.table('jadwal_penugasan')\
                                .delete()\
                                .eq('username_lh', username)\
                                .eq('nama_atraksi', nama_atraksi)\
                                .execute()

                    # 4. Ambil log dari trigger jika ada
                    log_result = supabase.table('log_rotasi_pelatih')\
                        .select('*')\
                        .eq('nama_atraksi', nama_atraksi)\
                        .in_('username_lh', pelatih_terpilih)\
                        .order('waktu', desc=True)\
                        .limit(1)\
                        .execute()

                    if log_result.data:
                        log = log_result.data[0]
                        messages.success(request, log['pesan'])

                    messages.success(request, 'Atraksi berhasil diperbarui!')
                    return redirect('attractions:list_atraksi')

                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
        else:
            jadwal_str = atraksi['fasilitas']['jadwal']
            jadwal_time = None
            try:
                jadwal_datetime = datetime.fromisoformat(jadwal_str.replace('Z', '+00:00'))
                jadwal_time = jadwal_datetime.time()
            except ValueError:
                try:
                    jadwal_time = datetime.strptime(jadwal_str, '%H:%M:%S').time()
                except ValueError:
                    try:
                        jadwal_time = datetime.strptime(jadwal_str, '%H:%M').time()
                    except ValueError:
                        jadwal_time = None

            current_pelatih_result = supabase.table('jadwal_penugasan').select('username_lh').eq('nama_atraksi', nama_atraksi).execute()
            initial_pelatih = [item['username_lh'] for item in current_pelatih_result.data]

            form = EditAtraksiForm(initial={
                'kapasitas_max': atraksi['fasilitas']['kapasitas_max'],
                'jadwal': jadwal_time,
                'pelatih': initial_pelatih
            })

        return render(request, 'atraksi_form.html', {
            'form': form,
            'edit_mode': True,
            'readonly_data': readonly_data,
        })

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('attractions:list_atraksi')

def hapus_atraksi(request, nama_atraksi):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    if request.method == 'POST':
        if request.POST.get('confirm') == 'ya':
            try:
                # Hapus dalam urutan yang benar untuk menghindari constraint violation
                # 1. Hapus jadwal penugasan
                supabase.table('jadwal_penugasan').delete().eq('nama_atraksi', nama_atraksi).execute()
                
                # 2. Hapus berpartisipasi
                supabase.table('berpartisipasi').delete().eq('nama_fasilitas', nama_atraksi).execute()
                
                # 3. Hapus atraksi
                supabase.table('reservasi').delete().eq('nama_fasilitas', nama_atraksi).execute()
                supabase.table('atraksi').delete().eq('nama_atraksi', nama_atraksi).execute()
                # 4. Hapus fasilitas
                result = supabase.table('fasilitas').delete().eq('nama', nama_atraksi).execute()
                
                if result.data:
                    messages.success(request, 'Atraksi berhasil dihapus!')
                else:
                    messages.error(request, 'Gagal menghapus atraksi.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return redirect('attractions:list_atraksi')

def edit_wahana(request, nama_wahana):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        # Ambil data wahana dan fasilitas secara terpisah
        wahana_result = supabase.table('wahana').select('*').eq('nama_wahana', nama_wahana).execute()
        fasilitas_result = supabase.table('fasilitas').select('*').eq('nama', nama_wahana).execute()

        if not wahana_result.data or not fasilitas_result.data:
            raise Http404("Wahana atau fasilitas tidak ditemukan")

        wahana = wahana_result.data[0]
        fasilitas = fasilitas_result.data[0]

        if request.method == 'POST':
            form = EditWahanaForm(request.POST)
            if form.is_valid():
                try:
                    # Hanya update data di tabel FASILITAS
                    fasilitas_update = {
                        'kapasitas_max': form.cleaned_data['kapasitas_max'],
                        'jadwal': form.cleaned_data['jadwal'].strftime('%Y-%m-%d %H:%M:%S')
                    }

                    fasilitas_result = supabase.table('fasilitas').update(fasilitas_update).eq('nama', nama_wahana).execute()

                    # Cek apakah update berhasil
                    if fasilitas_result.data and len(fasilitas_result.data) > 0:
                        messages.success(request, 'Wahana berhasil diperbarui!')
                        return redirect('attractions:list_wahana')
                    else:
                        messages.error(request, 'Gagal memperbarui wahana. Data tidak ditemukan.')

                except Exception as e:
                    print(f"Exception during update: {str(e)}")
                    messages.error(request, f'Error saat update: {str(e)}')
            else:
                print(f"Form errors: {form.errors}")
                messages.error(request, 'Form tidak valid. Silakan periksa input Anda.')
        else:
            # Convert jadwal string ke time object
            jadwal_str = fasilitas['jadwal']
            jadwal_time = None

            if jadwal_str:
                try:
                    if 'T' in str(jadwal_str):
                        jadwal_datetime = datetime.fromisoformat(str(jadwal_str).replace('Z', '+00:00'))
                        jadwal_time = jadwal_datetime.time()
                    else:
                        try:
                            jadwal_time = datetime.strptime(str(jadwal_str), '%H:%M:%S').time()
                        except ValueError:
                            jadwal_time = datetime.strptime(str(jadwal_str), '%H:%M').time()
                except Exception as e:
                    print(f"Error parsing jadwal: {jadwal_str}, Error: {str(e)}")
                    jadwal_time = None

            initial_data = {
                'nama_wahana': wahana['nama_wahana'],
                'kapasitas_max': fasilitas['kapasitas_max'],
                'jadwal': jadwal_time,
            }

            form = EditWahanaForm(initial=initial_data)

        readonly_data = {
            'nama_wahana': wahana['nama_wahana']
        }

        return render(request, 'wahana_form.html', {
            'form': form,
            'edit_mode': True,
            'readonly_data': readonly_data
        })

    except Exception as e:
        print(f"General exception: {str(e)}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('attractions:list_wahana')

def hapus_wahana(request, nama_wahana):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'admin_staff':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    if request.method == 'POST':
        if request.POST.get('confirm') == 'ya':
            try:
                # 1.Hapus wahana
                supabase.table('reservasi').delete().eq('nama_fasilitas', nama_wahana).execute()
                supabase.table('wahana').delete().eq('nama_wahana', nama_wahana).execute()
                
                # 2. Hapus fasilitas
                result = supabase.table('fasilitas').delete().eq('nama', nama_wahana).execute()
                if result.data:
                    messages.success(request, 'Wahana berhasil dihapus!')
                else:
                    messages.error(request, 'Gagal menghapus wahana.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return redirect('attractions:list_wahana')

DATA_ATRAKSI_TRAINER = [
    {
        'nama': 'Pertunjukan lumba-lumba',
        'lokasi': 'Area Akuatik',
        'kapasitas': 100,
        'jadwal': '10:00'
    },
    {
        'nama': 'Feeding time harimau',
        'lokasi': 'Zona Harimau',
        'kapasitas': 75,
        'jadwal': '11:30'
    },
    {
        'nama': 'Bird show',
        'lokasi': 'Amphitheater utama',
        'kapasitas': 150,
        'jadwal': '09:30'
    }
]
def list_atraksi_trainer(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'trainer':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        username_lh = request.session.get('username')
        
        penugasan_result = supabase.table('jadwal_penugasan').select('''
            nama_atraksi,
            tgl_penugasan
        ''').eq('username_lh', username_lh).execute()

        atraksi_list = []

        for item in penugasan_result.data:
            nama_atraksi = item['nama_atraksi']
            tgl_penugasan = item['tgl_penugasan']

            atraksi_result = supabase.table('atraksi').select('lokasi').eq('nama_atraksi', nama_atraksi).execute()
            fasilitas_result = supabase.table('fasilitas').select('kapasitas_max', 'jadwal').eq('nama', nama_atraksi).execute()

            if atraksi_result.data and fasilitas_result.data:
                lokasi = atraksi_result.data[0]['lokasi']
                kapasitas = fasilitas_result.data[0]['kapasitas_max']
                jadwal_raw = fasilitas_result.data[0]['jadwal']

                try:
                    jadwal_dt = datetime.fromisoformat(jadwal_raw.replace('Z', '+00:00'))
                    jadwal = jadwal_dt.strftime('%H:%M')
                except Exception:
                    jadwal = jadwal_raw

                atraksi_list.append({
                    'nama': nama_atraksi,
                    'lokasi': lokasi,
                    'kapasitas': kapasitas,
                    'jadwal': jadwal,
                    'tgl_penugasan': tgl_penugasan
                })

        return render(request, 'atraksi_list_trainer.html', {'data_atraksi': atraksi_list})

    except Exception as e:
        messages.error(request, f'Error mengambil data atraksi trainer: {str(e)}')
        return render(request, 'atraksi_list_trainer.html', {'data_atraksi': []})


def tambah_atraksi_trainer(request):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'trainer':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        lokasi = request.POST.get('lokasi')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        DATA_ATRAKSI_TRAINER.append({
            'nama': nama,
            'lokasi': lokasi,
            'kapasitas': kapasitas,
            'jadwal': jadwal,
        })
        return redirect('attractions:list_atraksi_trainer')
    return render(request, 'atraksi_form_trainer.html')

def edit_atraksi_trainer(request, nama_atraksi):
    current_username = request.session.get('username')
    user_role = get_user_role(current_username)

    if user_role != 'trainer':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini")
        return redirect('main:show_main')
    
    try:
        atraksi_result = supabase.table('atraksi').select('''
            nama_atraksi,
            lokasi,
            fasilitas!inner(
                jadwal,
                kapasitas_max
            )
        ''').eq('nama_atraksi', nama_atraksi).execute()

        if not atraksi_result.data:
            raise Http404("Atraksi tidak ditemukan")

        atraksi = atraksi_result.data[0]

        if request.method == 'POST':
            jadwal_str = request.POST.get('jadwal')
            try:
                jadwal_obj = datetime.strptime(jadwal_str, '%H:%M').time()
                supabase.table('fasilitas').update({
                    'jadwal': jadwal_obj.strftime('%Y-%m-%d %H:%M:%S')
                }).eq('nama', nama_atraksi).execute()

                messages.success(request, 'Jam atraksi berhasil diperbarui!')
                return redirect('attractions:list_atraksi_trainer')
            except Exception as e:
                messages.error(request, f'Error saat menyimpan jadwal: {str(e)}')

        else:
            jadwal_str = atraksi['fasilitas']['jadwal']
            jadwal_time = None
            if jadwal_str:
                try:
                    jadwal_datetime = datetime.fromisoformat(jadwal_str.replace('Z', '+00:00'))
                    jadwal_time = jadwal_datetime.time()
                except:
                    try:
                        jadwal_time = datetime.strptime(jadwal_str, '%H:%M:%S').time()
                    except:
                        jadwal_time = datetime.strptime(jadwal_str, '%H:%M').time()

        return render(request, 'atraksi_form_trainer.html', {
            'edit_mode': True,
            'nama_atraksi': atraksi['nama_atraksi'],
            'lokasi': atraksi['lokasi'],
            'kapasitas': atraksi['fasilitas']['kapasitas_max'],
            'jadwal': jadwal_time,
        })

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('attractions:list_atraksi_trainer')

def hapus_atraksi_trainer(request, index):
    DATA_ATRAKSI_TRAINER.pop(index)
    return redirect('attractions:list_atraksi_trainer')
