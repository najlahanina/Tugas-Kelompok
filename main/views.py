from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import random
import string
from django.contrib.auth.forms import PasswordChangeForm
from .forms import (
    RoleSelectionForm, VisitorRegistrationForm, VeterinarianRegistrationForm,
    StaffRegistrationForm, UserProfileUpdateForm, VisitorProfileUpdateForm, VeterinarianProfileUpdateForm
)
from .models import UserProfile, Visitor, Veterinarian, Staff

def show_main(request):
    return render(request, 'main.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('main:dashboard')  # Redirect to dashboard or main page
        else:
            messages.error(request, 'Username atau password salah')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('main:login')

def register_step1(request):
    """First step of registration - select role"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            request.session['selected_role'] = role
            return redirect('main:register_step2')
    else:
        form = RoleSelectionForm()
    
    return render(request, 'register_role.html', {'form': form})

def register_step2(request):
    """Second step of registration - fill form based on role"""
    role = request.session.get('selected_role')
    
    if not role:
        return redirect('main:register_step1')
    
    if role == 'visitor':
        return register_visitor(request)
    elif role == 'veterinarian':
        return register_veterinarian(request)
    elif role == 'staff':
        return register_staff(request, role)
    else:
        return redirect('main:register_step1')

def register_visitor(request):
    if request.method == 'POST':
        form = VisitorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            profile = UserProfile.objects.create(
                user=user,
                middle_name=form.cleaned_data['middle_name'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                birth_date=form.cleaned_data['birth_date'],
                role='visitor'
            )
            
            Visitor.objects.create(profile=profile)
            
            login(request, user)
            return redirect('main:dashboard')
    else:
        form = VisitorRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'Pengunjung'})

def register_veterinarian(request):
    if request.method == 'POST':
        form = VeterinarianRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            profile = UserProfile.objects.create(
                user=user,
                middle_name=form.cleaned_data['middle_name'],
                phone_number=form.cleaned_data['phone_number'],
                role='veterinarian'
            )
            
            specialization = form.cleaned_data['specialization']
            other_specialization = None
            if specialization == 'other':
                other_specialization = form.cleaned_data['other_specialization']
            
            Veterinarian.objects.create(
                profile=profile,
                certification_number=form.cleaned_data['certification_number'],
                specialization=specialization,
                other_specialization=other_specialization
            )
            
            login(request, user)
            return redirect('main:dashboard')
    else:
        form = VeterinarianRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'Dokter Hewan'})

def register_staff(request, staff_role=None):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Get staff role from the form
            staff_role = form.cleaned_data['staff_role']
            
            profile = UserProfile.objects.create(
                user=user,
                middle_name=form.cleaned_data['middle_name'],
                phone_number=form.cleaned_data['phone_number'],
                role=staff_role
            )
            
            staff_id = form.cleaned_data['staff_id']
            Staff.objects.create(
                profile=profile,
                staff_id=staff_id
            )
            
            login(request, user)
            return redirect('main:dashboard')  # Note: using 'main:dashboard' namespace
    else:
        form = StaffRegistrationForm(initial={'staff_role': staff_role} if staff_role else {})
    
    return render(request, 'register.html', {
        'form': form, 
        'role': 'Staff',
    })

def generate_staff_id(request):
    """AJAX endpoint to generate staff ID"""
    role = request.GET.get('role')
    prefix_map = {
        'animal_keeper': 'PJH',
        'admin_staff': 'ADM',
        'trainer': 'PLP'
    }
    prefix = prefix_map.get(role, 'STF')
    random_suffix = ''.join(random.choices(string.digits, k=3))
    staff_id = f"{prefix}{random_suffix}"
    return JsonResponse({'staff_id': staff_id})

@login_required
def dashboard(request):
    """Dashboard view - displays different content based on user role"""
    try:
        profile = request.user.profile
        role = profile.role
        
        context = {
            'role': role,
            'user': request.user
        }
        
        return render(request, 'dashboard.html', context)
    except UserProfile.DoesNotExist:
        # Handle case where user doesn't have a profile
        messages.error(request, 'Profil pengguna tidak ditemukan')
        return redirect('main:login')
    
@login_required
def profile_settings(request):
    """View for updating user profile information based on their role"""
    try:
        profile = request.user.profile
        role = profile.role
        
        if request.method == 'POST':
            profile_form = UserProfileUpdateForm(request.POST, instance=profile)
            
            # Role-specific forms
            role_form = None
            if role == 'visitor':
                try:
                    visitor_profile = profile.visitor_profile
                    role_form = VisitorProfileUpdateForm(request.POST, instance=visitor_profile)
                except:
                    messages.error(request, 'Profil pengunjung tidak ditemukan')
            elif role == 'veterinarian':
                try:
                    vet_profile = profile.vet_profile
                    role_form = VeterinarianProfileUpdateForm(request.POST, instance=vet_profile)
                except:
                    messages.error(request, 'Profil dokter hewan tidak ditemukan')
            
            forms_valid = profile_form.is_valid()
            if role_form:
                forms_valid = forms_valid and role_form.is_valid()
                
            if forms_valid:
                # Update user model fields
                user = request.user
                user.email = profile_form.cleaned_data['email']
                user.first_name = profile_form.cleaned_data['first_name']
                if 'last_name' in profile_form.cleaned_data:
                    user.last_name = profile_form.cleaned_data['last_name']
                user.save()
                
                profile_form.save()
                
                # Save role-specific form if exists
                if role_form:
                    role_form.save()
                    
                messages.success(request, 'Profil berhasil diperbarui')
                return redirect('main:dashboard')
        else:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'middle_name': profile.middle_name,
                'phone_number': profile.phone_number,
            }
            
            profile_form = UserProfileUpdateForm(instance=profile, initial=initial_data)
            role_form = None
            
            if role == 'visitor':
                try:
                    visitor_profile = profile.visitor_profile
                    role_form = VisitorProfileUpdateForm(instance=visitor_profile)
                except:
                    pass
            elif role == 'veterinarian':
                try:
                    vet_profile = profile.vet_profile
                    role_form = VeterinarianProfileUpdateForm(instance=vet_profile)
                except:
                    pass
        
        context = {
            'profile_form': profile_form,
            'role_form': role_form,
            'role': role,
            'user': request.user,
        }
        
        return render(request, 'profile_settings.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil pengguna tidak ditemukan')
        return redirect('main:dashboard')

@login_required
def change_password(request):
    """View for changing user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Password berhasil diubah')
            return redirect('main:dashboard')
        else:
            messages.error(request, 'Silakan perbaiki kesalahan di bawah ini.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})