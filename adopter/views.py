import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.defaulttags import register
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from supabase_utils import (
    get_all_adopsi, get_all_hewan, get_all_adopter,
    get_all_individu, get_all_organisasi, get_all_catatan_medis,
    get_hewan_by_id, get_individu_by_id, get_organisasi_by_id,
    get_adopter_by_username
)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def get_adopter_id_from_user(username):
    # Get adopter data based on username
    adopter = get_adopter_by_username(username)
    if adopter:
        return adopter['id_adopter']
    return None

def load_data():
    return {
        'adopters': get_all_adopter(),
        'individus': get_all_individu(),
        'organisasis': get_all_organisasi(),
        'catatan_kesehatans': get_all_catatan_medis(),
        'animals': get_all_hewan(),
        'adoptions': get_all_adopsi()
    }

def get_adopter_info(adopter_id, data):
    for individu in data['individus']:
        if individu['id_adopter'] == adopter_id:
            for adopter in data['adopters']:
                if adopter['id_adopter'] == adopter_id:
                    return {
                        'type': 'individu',
                        'name': individu['nama'],
                        'nik': individu['nik'],
                        'username': adopter['username_adopter'],
                        'total_kontribusi': adopter['total_kontribusi']
                    }

    # Check if adopter is an organization
    for organisasi in data['organisasis']:
        if organisasi['id_adopter'] == adopter_id:
            for adopter in data['adopters']:
                if adopter['id_adopter'] == adopter_id:
                    return {
                        'type': 'organisasi',
                        'name': organisasi['nama_organisasi'],
                        'npp': organisasi['npp'],
                        'username': adopter['username_adopter'],
                        'total_kontribusi': adopter['total_kontribusi']
                    }

    return None

def get_animal_info(animal_id, data):
    for animal in data['animals']:
        if animal['id'] == animal_id:
            return animal
    return None

def get_adoption_info(adopter_id, animal_id, data):
    for adoption in data['adoptions']:
        if adoption['id_adopter'] == adopter_id and adoption['id_hewan'] == animal_id:
            return adoption
    return None

def get_health_records(animal_id, data):
    health_records = []
    for record in data['catatan_kesehatans']:
        if record['id_hewan'] == animal_id:
            health_records.append(record)
    return health_records

def get_adopted_animals(adopter_id, data):
    adopted_animals = []
    for adoption in data['adoptions']:
        if adoption['id_adopter'] == adopter_id:
            animal = get_animal_info(adoption['id_hewan'], data)
            if animal:
                adopted_animals.append({
                    'animal': animal,
                    'adoption': adoption
                })
    return adopted_animals

@login_required
def adoption_program(request):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    adopter_info = get_adopter_info(adopter_id, data)
    adopted_animals = get_adopted_animals(adopter_id, data)

    # Get health records for all animals
    health_records = []
    for record in data['catatan_kesehatans']:
        health_records.append(record)

    context = {
        'adopter_info': adopter_info,
        'adopted_animals': adopted_animals,
        'health_records': health_records
    }

    return render(request, 'adopter/adoption_program.html', context)

@login_required
def animal_detail(request, animal_id):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    animal = get_animal_info(animal_id, data)
    adoption = get_adoption_info(adopter_id, animal_id, data)

    context = {
        'animal': animal,
        'adoption': adoption
    }

    return render(request, 'adopter/adoption_program.html', context)

@login_required
def adoption_certificate(request, animal_id):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    animal = get_animal_info(animal_id, data)
    adoption = get_adoption_info(adopter_id, animal_id, data)
    adopter_info = get_adopter_info(adopter_id, data)

    context = {
        'animal': animal,
        'adoption': adoption,
        'adopter_info': adopter_info
    }

    return render(request, 'adopter/adoption_program.html', context)

@login_required
def animal_health_report(request, animal_id):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    animal = get_animal_info(animal_id, data)
    health_records = get_health_records(animal_id, data)

    context = {
        'animal': animal,
        'health_records': health_records
    }

    return render(request, 'adopter/adoption_program.html', context)

@login_required
def extend_adoption(request, animal_id):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    animal = get_animal_info(animal_id, data)
    adoption = get_adoption_info(adopter_id, animal_id, data)
    adopter_info = get_adopter_info(adopter_id, data)

    if request.method == 'POST':
        return redirect('adopter:adoption_program')

    context = {
        'animal': animal,
        'adoption': adoption,
        'adopter_info': adopter_info,
        'adopter_type': adopter_info['type'] if adopter_info else None
    }

    return render(request, 'adopter/adoption_program.html', context)

@login_required
def stop_adoption(request, animal_id):
    adopter_id = get_adopter_id_from_user(request.user.username)
    if not adopter_id:
        return HttpResponseForbidden("Access denied. User is not an adopter.")

    data = load_data()
    animal = get_animal_info(animal_id, data)

    if request.method == 'POST':
        return redirect('adopter:adoption_program')

    context = {
        'animal': animal
    }

    return render(request, 'adopter/adoption_program.html', context)
