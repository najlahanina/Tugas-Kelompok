from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Animal
from .forms import AnimalForm

class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'

class AnimalCreateView(CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    success_url = reverse_lazy('animal-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'FORM TAMBAH DATA SATWA'
        context['is_add'] = True
        return context

class AnimalUpdateView(UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    success_url = reverse_lazy('animal-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'FORM EDIT DATA SATWA'
        context['is_add'] = False
        return context

class AnimalDeleteView(DeleteView):
    model = Animal
    success_url = reverse_lazy('animal-list')
    template_name = 'animals/animal_confirm_delete.html'