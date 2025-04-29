from django.shortcuts import render, redirect
from .forms import AtraksiForm, WahanaForm, EditAtraksiForm, EditWahanaForm
from .models import Atraksi, Wahana, Fasilitas
from animals.models import Animal
from django.utils import timezone

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

DATA_WAHANA = [
    {
        'nama': 'Taman Air Mini',
        'kapasitas': 100,
        'jadwal': '10:00',
        'peraturan': ['Dilarang Berenang', 'Dilarang membawa makanan']
    },
    {
        'nama': 'Area Petualangan Anak',
        'kapasitas': 75,
        'jadwal': '11:30',
        'peraturan': ['Dilarang memanjat pagar']
    }
]

def list_atraksi(request):
    return render(request, 'atraksi_list.html', {'data_atraksi': DATA_ATRAKSI})

def tambah_atraksi(request):
    if request.method == 'POST':
        form = AtraksiForm(request.POST)
        if form.is_valid():
            DATA_ATRAKSI.append({
                'nama': form.cleaned_data['nama_atraksi'],
                'lokasi': form.cleaned_data['lokasi'],
                'kapasitas': form.cleaned_data['kapasitas_max'],
                'jadwal': form.cleaned_data['jadwal'].strftime('%H:%M'),
                'hewan': form.cleaned_data['hewan'],
                'pelatih': form.cleaned_data['pelatih']
            })
            return redirect('attractions:list_atraksi')
    else:
        form = AtraksiForm()
    return render(request, 'atraksi_form.html', {'form': form})

def list_wahana(request):
    return render(request, 'wahana_list.html', {'data_wahana': DATA_WAHANA})

def tambah_wahana(request):
    if request.method == 'POST':
        form = WahanaForm(request.POST)
        if form.is_valid():
            DATA_WAHANA.append({
                'nama': form.cleaned_data['nama_wahana'],
                'kapasitas': form.cleaned_data['kapasitas_max'],
                'jadwal': form.cleaned_data['jadwal'].strftime('%H:%M'),
                'peraturan': form.cleaned_data['peraturan'].split('\n')
            })
            return redirect('attractions:list_wahana')
    else:
        form = WahanaForm()
    return render(request, 'wahana_form.html', {'form': form})

def edit_atraksi(request, index):
    atraksi = DATA_ATRAKSI[index]
    if request.method == 'POST':
        form = EditAtraksiForm(request.POST)
        if form.is_valid():
            DATA_ATRAKSI[index]['kapasitas'] = form.cleaned_data['kapasitas_max']
            DATA_ATRAKSI[index]['jadwal'] = form.cleaned_data['jadwal'].strftime('%H:%M')
            return redirect('attractions:list_atraksi')
    else:
        form = EditAtraksiForm(initial={
            'kapasitas_max': atraksi['kapasitas'],
            'jadwal': atraksi['jadwal'],
        })
    
    # Menambahkan data atraksi yang tidak bisa diubah untuk tampilan
    readonly_data = {
        'nama_atraksi': atraksi['nama'],
        'lokasi': atraksi['lokasi'],
        'hewan': atraksi['hewan'],
        'pelatih': atraksi['pelatih'],
    }
    
    return render(request, 'atraksi_form.html', {
        'form': form, 
        'edit_mode': True,
        'readonly_data': readonly_data
    })


def hapus_atraksi(request, index):
    if request.method == 'POST':
        if request.POST.get('confirm') == 'ya':
            DATA_ATRAKSI.pop(index)
        return redirect('attractions:list_atraksi')
    return redirect('attractions:list_atraksi')

def edit_wahana(request, index):
    wahana = DATA_WAHANA[index]
    
    if request.method == 'POST':
        form = EditWahanaForm(request.POST)
        if form.is_valid():
            DATA_WAHANA[index] = {
                'nama': form.cleaned_data['nama_wahana'],
                'kapasitas': form.cleaned_data['kapasitas_max'],
                'jadwal': form.cleaned_data['jadwal'].strftime('%H:%M'),
                'peraturan': form.cleaned_data['peraturan'],
            }
            return redirect('attractions:list_wahana')
    else:
        initial_data = {
            'kapasitas_max': wahana['kapasitas'],
            'jadwal': wahana['jadwal'],
        }
        form = EditWahanaForm(initial=initial_data)
    
    readonly_data = {
        'nama_wahana': wahana['nama'] 
    }
    return render(request, 'wahana_form.html', {
        'form': form,
        'edit_mode': True,
        'readonly_data': readonly_data
    })

def hapus_wahana(request, index):
    if request.method == 'POST':
        if request.POST.get('confirm') == 'ya':
            DATA_WAHANA.pop(index)
        return redirect('attractions:list_wahana')
    return redirect('attractions:list_wahana')