import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaulttags import register
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from supabase_client import supabase
from django.http import JsonResponse


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def load_data():
    base_dir = os.path.dirname(__file__)

    adoption_json_path = os.path.join(base_dir, 'data', 'adoption_data.json')
    with open(adoption_json_path, 'r', encoding='utf-8') as file:
        adoption_data = json.load(file)

    animals_json_path = os.path.join(base_dir, 'data', 'animals_data.json')
    with open(animals_json_path, 'r', encoding='utf-8') as file:
        animals_data = json.load(file)

    adopter_base_dir = os.path.dirname(os.path.dirname(__file__))
    adopter_json_path = os.path.join(adopter_base_dir, 'adopter', 'data', 'adopter_data.json')
    with open(adopter_json_path, 'r', encoding='utf-8') as file:
        adopter_data = json.load(file)

    individu_json_path = os.path.join(adopter_base_dir, 'adopter', 'data', 'individu_data.json')
    with open(individu_json_path, 'r', encoding='utf-8') as file:
        individu_data = json.load(file)

    organisasi_json_path = os.path.join(adopter_base_dir, 'adopter', 'data', 'organisasi_data.json')
    with open(organisasi_json_path, 'r', encoding='utf-8') as file:
        organisasi_data = json.load(file)

    return {
        'adoptions': adoption_data.get('adoptions', []),
        'animals': animals_data.get('animals', []),
        'adopters': adopter_data.get('adopter', []),
        'individus': individu_data.get('individu', []),
        'organisasis': organisasi_data.get('organisasi', [])
    }

def get_adopter_info(adopter_id, data):

    for individu in data['individus']:
        if individu['id_adopter'] == adopter_id:
            # Found individual adopter
            for adopter in data['adopters']:
                if adopter['id_adopter'] == adopter_id:
                    return {
                        'type': 'individu',
                        'name': individu['nama'],
                        'nik': individu['nik'],
                        'username': adopter['username_adopter'],
                        'total_kontribusi': adopter['total_kontribusi']
                    }

    for organisasi in data['organisasis']:
        if organisasi['id_adopter'] == adopter_id:
            # Found organization adopter
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

def get_adoption_history(adopter_id, data):
    adoption_history = []
    for adoption in data['adoptions']:
        if adoption['id_adopter'] == adopter_id:
            animal = get_animal_info(adoption['id_hewan'], data)
            if animal:
                adoption_history.append({
                    'animal': animal,
                    'adoption': adoption
                })
    return adoption_history

def calculate_total_contribution(adopter_id, data):
    total = 0
    for adoption in data['adoptions']:
        if adoption['id_adopter'] == adopter_id:
            total += int(adoption['kontribusi_finansial'])
    return total

def adoption_admin_page(request):
    base_dir = os.path.dirname(__file__)

    adoption_json_path = os.path.join(base_dir, 'data', 'adoption_data.json')
    with open(adoption_json_path, 'r', encoding='utf-8') as file:
        adoption_data = json.load(file)

    animals_json_path = os.path.join(base_dir, 'data', 'animals_data.json')
    with open(animals_json_path, 'r', encoding='utf-8') as file:
        animals_data = json.load(file)

    animals = animals_data.get('animals', [])

    adoptions = adoption_data.get('adoptions', [])

    adoption_info = {}
    for adoption in adoptions:
        animal_id = adoption['id_hewan']

        adoption_info[animal_id] = {
            'status': 'Diadopsi',
            'adopter': f"Adopter ID: {adoption['id_adopter']}",
            'adoption': {
                'start_date': adoption['tgl_mulai_adopsi'],
                'end_date': adoption['tgl_berhenti_adopsi'],
                'contribution': f"Rp {int(adoption['kontribusi_finansial']):,}",
                'payment_status': adoption['status_pembayaran']
            }
        }

    for animal in animals:
        if animal['id'] not in adoption_info:
            adoption_info[animal['id']] = {
                'status': 'Tidak Diadopsi',
                'adopter': None,
                'adoption': None
            }

    # Serialize the data for JavaScript
    animals_json = json.dumps(animals)
    adoption_info_json = json.dumps(adoption_info, cls=DjangoJSONEncoder)

    context = {
        'animals': animals,
        'adoption_info': adoption_info,
        'animals_json': animals_json,
        'adoption_info_json': adoption_info_json,
    }

    return render(request, 'main_page_adoption_admin.html', context)

def adopter_list(request):

    data = load_data()

    adopter_list = []
    for adopter in data['adopters']:
        adopter_id = adopter['id_adopter']
        adopter_info = get_adopter_info(adopter_id, data)

        if adopter_info:
            total_contribution = calculate_total_contribution(adopter_id, data)

            adopter_list.append({
                'id': adopter_id,
                'name': adopter_info['name'],
                'type': adopter_info['type'],
                'username': adopter_info['username'],
                'total_kontribusi': total_contribution
            })

    adopter_list.sort(key=lambda x: x['total_kontribusi'], reverse=True)

    top_adopters = adopter_list[:5]

    context = {
        'adopter_list': adopter_list,
        'top_adopters': top_adopters
    }

    return render(request, 'administrative_staff/adopter_list.html', context)

def adopter_detail(request, adopter_id):

    data = load_data()

    adopter_info = get_adopter_info(adopter_id, data)

    if not adopter_info:
        return HttpResponse("Adopter not found", status=404)

    adoption_history = get_adoption_history(adopter_id, data)

    context = {
        'adopter_info': adopter_info,
        'adoption_history': adoption_history
    }

    return render(request, 'administrative_staff/adopter_detail.html', context)

def get_adoption_data(request):
    adoption_data = supabase.table('adoption').select('*').execute()
    return JsonResponse(adoption_data)

def get_animal_data(request):
    animal_data = supabase.table('animals').select('*').execute()
    return JsonResponse(animal_data)


