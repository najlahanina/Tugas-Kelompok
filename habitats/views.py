from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Habitat
from .forms import HabitatForm

class HabitatListView(ListView):
    model = Habitat
    template_name = 'habitats/habitat_list.html'
    context_object_name = 'habitats'

class HabitatDetailView(DetailView):
    model = Habitat
    template_name = 'habitats/habitat_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['animals'] = self.object.animal_set.all()
        return context

class HabitatCreateView(CreateView):
    model = Habitat
    form_class = HabitatForm
    template_name = 'habitats/habitat_form.html'
    success_url = reverse_lazy('habitats:habitat_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'FORM TAMBAH HABITAT'
        context['is_add'] = True
        return context

class HabitatUpdateView(UpdateView):
    model = Habitat
    form_class = HabitatForm
    template_name = 'habitats/habitat_form.html'
    success_url = reverse_lazy('habitats:habitat_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'FORM EDIT HABITAT'
        context['is_add'] = False
        return context

class HabitatDeleteView(DeleteView):
    model = Habitat
    success_url = reverse_lazy('habitats:habitat_list')
    template_name = 'habitats/habitat_confirm_delete.html'