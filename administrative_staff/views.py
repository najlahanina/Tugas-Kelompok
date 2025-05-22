import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaulttags import register
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supabase_utils import (
    get_all_adopsi, get_all_hewan, get_all_adopter,
    get_all_individu, get_all_organisasi, get_adopsi_by_id,
    get_hewan_by_id, get_individu_by_id, get_organisasi_by_id,
    create_complete_adopter, create_adopsi, update_adopsi,
    delete_adopter
)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def load_data():
    return {
        'adoptions': get_all_adopsi(),
        'animals': get_all_hewan(),
        'adopters': get_all_adopter(),
        'individus': get_all_individu(),
        'organisasis': get_all_organisasi()
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
    animals = get_all_hewan()
    adoptions = get_all_adopsi()

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
    current_date = datetime.now()
    one_year_ago = current_date - timedelta(days=365)

    individual_adopters = []
    organization_adopters = []
    top_adopters = []

    # Process individual adopters
    for individu in data['individus']:
        adopter_id = individu['id_adopter']
        # Get adopter base info
        adopter_base = next((a for a in data['adopters'] if a['id_adopter'] == adopter_id), None)
        
        if adopter_base:
            active_adoptions = []
            yearly_contribution = 0
            
            # Calculate contributions
            for adoption in data['adoptions']:
                if adoption['id_adopter'] == adopter_id:
                    start_date = datetime.strptime(adoption['tgl_mulai_adopsi'], '%Y-%m-%d')
                    end_date = datetime.strptime(adoption['tgl_berhenti_adopsi'], '%Y-%m-%d')
                    
                    if end_date >= current_date:
                        active_adoptions.append(adoption)
                    
                    if adoption['status_pembayaran'] == 'Lunas' and start_date >= one_year_ago:
                        yearly_contribution += int(adoption['kontribusi_finansial'])

            adopter_data = {
                'id': adopter_id,
                'name': individu['nama'],
                'type': 'individu',
                'username': adopter_base['username_adopter'],
                'total_kontribusi': adopter_base['total_kontribusi'],
                'yearly_kontribusi': yearly_contribution,
                'has_active_adoptions': len(active_adoptions) > 0,
                'nik': individu['nik']
            }
            
            individual_adopters.append(adopter_data)
            if yearly_contribution > 0:
                top_adopters.append(adopter_data)

    # Process organization adopters
    for organisasi in data['organisasis']:
        adopter_id = organisasi['id_adopter']
        # Get adopter base info
        adopter_base = next((a for a in data['adopters'] if a['id_adopter'] == adopter_id), None)
        
        if adopter_base:
            active_adoptions = []
            yearly_contribution = 0
            
            # Calculate contributions
            for adoption in data['adoptions']:
                if adoption['id_adopter'] == adopter_id:
                    start_date = datetime.strptime(adoption['tgl_mulai_adopsi'], '%Y-%m-%d')
                    end_date = datetime.strptime(adoption['tgl_berhenti_adopsi'], '%Y-%m-%d')
                    
                    if end_date >= current_date:
                        active_adoptions.append(adoption)
                    
                    if adoption['status_pembayaran'] == 'Lunas' and start_date >= one_year_ago:
                        yearly_contribution += int(adoption['kontribusi_finansial'])

            adopter_data = {
                'id': adopter_id,
                'name': organisasi['nama_organisasi'],
                'type': 'organisasi',
                'username': adopter_base['username_adopter'],
                'total_kontribusi': adopter_base['total_kontribusi'],
                'yearly_kontribusi': yearly_contribution,
                'has_active_adoptions': len(active_adoptions) > 0,
                'npp': organisasi['npp']
            }
            
            organization_adopters.append(adopter_data)
            if yearly_contribution > 0:
                top_adopters.append(adopter_data)

    # Sort adopters by contribution
    individual_adopters.sort(key=lambda x: x['total_kontribusi'], reverse=True)
    organization_adopters.sort(key=lambda x: x['total_kontribusi'], reverse=True)
    top_adopters.sort(key=lambda x: x['yearly_kontribusi'], reverse=True)
    top_adopters = top_adopters[:5]

    context = {
        'individual_adopters': individual_adopters,
        'organization_adopters': organization_adopters,
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

@csrf_exempt
def submit_adoption(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        adopter_type = data.get('adopter_type')
        username = data.get('username')
        animal_id = data.get('animal_id')
        
        adopter_data = {
            'username_adopter': username,
            'total_kontribusi': 0
        }
        
        if adopter_type == 'individu':
            type_data = {
                'nama': data.get('nama'),
                'nik': data.get('nik')
            }
            is_individual = True
        else:
            type_data = {
                'nama_organisasi': data.get('nama_organisasi'),
                'npp': data.get('npp')
            }
            is_individual = False
            
        new_adopter = create_complete_adopter(
            adopter_data=adopter_data,
            type_data=type_data,
            is_individual=is_individual
        )
        
        adoption_data = {
            'id_adopter': new_adopter['id_adopter'],
            'id_hewan': animal_id,
            'tgl_mulai_adopsi': data.get('start_date'),
            'tgl_berhenti_adopsi': data.get('end_date'),
            'kontribusi_finansial': data.get('kontribusi'),
            'status_pembayaran': 'Belum Lunas'  
        }
        
        new_adoption = create_adopsi(adoption_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Adopsi berhasil didaftarkan',
            'data': new_adoption
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
def update_payment_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        adoption_id = data.get('adoption_id')
        new_status = data.get('status')
        
        updated_adoption = update_adopsi(
            adoption_id,
            {'status_pembayaran': new_status}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Status pembayaran berhasil diperbarui',
            'data': updated_adoption
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
def delete_adopter_view(request, adopter_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = load_data()
        current_date = datetime.now()
        
        for adoption in data['adoptions']:
            if adoption['id_adopter'] == adopter_id:
                end_date = datetime.strptime(adoption['tgl_berhenti_adopsi'], '%Y-%m-%d')
                if end_date >= current_date:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tidak dapat menghapus adopter yang masih aktif mengadopsi satwa.'
                    }, status=400)
        
        delete_adopter(adopter_id)
        
        return JsonResponse({
            'success': True,
            'message': 'Adopter berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

