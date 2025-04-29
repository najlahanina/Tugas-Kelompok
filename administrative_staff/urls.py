from django.urls import path
from . import views

app_name = 'administrative_staff'

urlpatterns = [
    path('adoption-admin/', views.adoption_admin_page, name='adoption_admin'),
    path('adopter-list/', views.adopter_list, name='adopter_list'),
    path('adopter-detail/<str:adopter_id>/', views.adopter_detail, name='adopter_detail'),
]
