from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from .forms import AnimalForm

# Data Hardcode
animals_data = [
    {'id': 1, 'name': 'Simba', 'species': 'Singa', 'origin': 'Afrika', 'birth_date': '2018-05-12', 'health_status': 'Sehat', 'habitat': 'Savana', 'photo_url': '[foto simba]'},
    {'id': 2, 'name': 'Melly', 'species': 'Gajah', 'origin': 'Sumatra', 'birth_date': '2015-09-22', 'health_status': 'Dalam Pemantauan', 'habitat': 'Hutan Tropis', 'photo_url': '[foto melly]'},
    {'id': 3, 'name': 'Rio', 'species': 'Harimau', 'origin': 'Kalimantan', 'birth_date': '2015-09-22', 'health_status': 'Sakit', 'habitat': 'Hutan Tropis', 'photo_url': '[foto rio]'},
    {'id': 4, 'name': 'Nala', 'species': 'Zebra', 'origin': 'Afrika', 'birth_date': '2020-03-01', 'health_status': 'Sehat', 'habitat': 'Savana', 'photo_url': '[foto nala]'},
    {'id': 5, 'name': 'Bimo', 'species': 'Orangutan', 'origin': 'Kalimantan', 'birth_date': '2016-07-19', 'health_status': 'Sehat', 'habitat': 'Hutan Tropis', 'photo_url': '[foto bimo]'}
]

class AnimalListView(ListView):
    # Tidak menggunakan model, hanya menggunakan data statis
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'

    def get_queryset(self):
        return animals_data

class AnimalCreateView(View):
    template_name = 'animals/animal_form.html'

    def get(self, request):
        form = AnimalForm()
        context = {
            'form': form,
            'title': 'FORM TAMBAH DATA SATWA',
            'is_add': True
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = AnimalForm(request.POST)
        if form.is_valid():
            # Skip saving data, directly redirect
            return HttpResponseRedirect(reverse_lazy('animals:animal_list'))
        context = {
            'form': form,
            'title': 'FORM TAMBAH DATA SATWA',
            'is_add': True
        }
        return render(request, self.template_name, context)
    
class AnimalUpdateView(View):
    template_name = 'animals/animal_form.html'

    def get(self, request, pk):
        # Ambil objek berdasarkan ID dari data statis
        animal = next((item for item in animals_data if item["id"] == pk), None)
        
        if animal is None:
            return redirect('animals:animal_list')

        form = AnimalForm(initial=animal)  # Isi form dengan data statis
        context = {
            'form': form,
            'title': 'FORM EDIT DATA SATWA',
            'is_add': False,
            'animal': animal
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        # Ambil objek berdasarkan ID dari data statis
        animal = next((item for item in animals_data if item["id"] == pk), None)

        if animal is None:
            return redirect('animals:animal_list')

        form = AnimalForm(request.POST)
        if form.is_valid():
            # Lewati update data, langsung redirect
            return HttpResponseRedirect(reverse_lazy('animals:animal_list'))

        context = {
            'form': form,
            'title': 'FORM EDIT DATA SATWA',
            'is_add': False,
            'animal': animal
        }
        return render(request, self.template_name, context)
    
class AnimalDeleteView(DeleteView):
    template_name = 'animals/animal_confirm_delete.html'

    def get(self, request, pk):
        # Temukan data berdasarkan ID dari data statis
        animal = next((item for item in animals_data if item["id"] == pk), None)
        return render(request, 'animals/animal_confirm_delete.html', {'object': animal})

    def post(self, request, pk):
        # Lewati penghapusan data, langsung redirect
        return redirect('animals:animal_list')
