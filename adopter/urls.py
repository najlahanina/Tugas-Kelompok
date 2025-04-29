from django.urls import path
from . import views

app_name = 'adopter'

urlpatterns = [
    path('adoption-program/', views.adoption_program, name='adoption_program'),
    path('animal-detail/<str:animal_id>/', views.animal_detail, name='animal_detail'),
    path('adoption-certificate/<str:animal_id>/', views.adoption_certificate, name='adoption_certificate'),
    path('animal-health-report/<str:animal_id>/', views.animal_health_report, name='animal_health_report'),
    path('extend-adoption/<str:animal_id>/', views.extend_adoption, name='extend_adoption'),
    path('stop-adoption/<str:animal_id>/', views.stop_adoption, name='stop_adoption'),
]
