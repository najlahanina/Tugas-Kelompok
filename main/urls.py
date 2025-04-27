from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.show_main, name='show_main'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_step1, name='register_step1'),
    path('register/form/', views.register_step2, name='register_step2'),
    path('generate-staff-id/', views.generate_staff_id, name='generate_staff_id'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
