import json
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def load_data():
    base_dir = os.path.dirname(__file__)

    adopter_json_path = os.path.join(base_dir, 'data', 'adopter_data.json')
    with open(adopter_json_path, 'r', encoding='utf-8') as file:
        adopter_data = json.load(file)

    individu_json_path = os.path.join(base_dir, 'data', 'individu_data.json')
    with open(individu_json_path, 'r', encoding='utf-8') as file:
        individu_data = json.load(file)

    organisasi_json_path = os.path.join(base_dir, 'data', 'organisasi_data.json')
    with open(organisasi_json_path, 'r', encoding='utf-8') as file:
        organisasi_data = json.load(file)

    catatan_kesehatan_json_path = os.path.join(base_dir, 'data', 'catatan_kesehatan_data.json')
    with open(catatan_kesehatan_json_path, 'r', encoding='utf-8') as file:
        catatan_kesehatan_data = json.load(file)

    admin_base_dir = os.path.dirname(os.path.dirname(__file__))
    animals_json_path = os.path.join(admin_base_dir, 'administrative_staff', 'data', 'animals_data.json')
    with open(animals_json_path, 'r', encoding='utf-8') as file:
        animals_data = json.load(file)

    adoption_json_path = os.path.join(admin_base_dir, 'administrative_staff', 'data', 'adoption_data.json')
    with open(adoption_json_path, 'r', encoding='utf-8') as file:
        adoption_data = json.load(file)

    return {
        'adopters': adopter_data.get('adopter', []),
        'individus': individu_data.get('individu', []),
        'organisasis': organisasi_data.get('organisasi', []),
        'catatan_kesehatans': catatan_kesehatan_data.get('catata_kesehatan', []),
        'animals': animals_data.get('animals', []),
        'adoptions': adoption_data.get('adoptions', [])
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

def adoption_program(request):

    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"

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

def animal_detail(request, animal_id):
    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"
    data = load_data()
    animal = get_animal_info(animal_id, data)
    adoption = get_adoption_info(adopter_id, animal_id, data)

    context = {
        'animal': animal,
        'adoption': adoption
    }

    return render(request, 'adopter/adoption_program.html', context)

def adoption_certificate(request, animal_id):
    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"
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

def animal_health_report(request, animal_id):
    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"
    data = load_data()
    animal = get_animal_info(animal_id, data)
    health_records = get_health_records(animal_id, data)

    context = {
        'animal': animal,
        'health_records': health_records
    }

    return render(request, 'adopter/adoption_program.html', context)

def extend_adoption(request, animal_id):
    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"
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

def stop_adoption(request, animal_id):
    adopter_id = "5a1f43e5-b1e6-4c5c-bc5a-111111111111"
    data = load_data()
    animal = get_animal_info(animal_id, data)

    if request.method == 'POST':
        return redirect('adopter:adoption_program')

    context = {
        'animal': animal
    }

    return render(request, 'adopter/adoption_program.html', context)
