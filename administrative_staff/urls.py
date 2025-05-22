from django.urls import path
from . import views

app_name = 'administrative_staff'

urlpatterns = [
    path('adoption-admin/', views.adoption_admin_page, name='adoption_admin'),
    path('adopter-list/', views.adopter_list, name='adopter_list'),
    path('adopter-detail/<str:adopter_id>/', views.adopter_detail, name='adopter_detail'),
    path('submit-adoption/', views.submit_adoption, name='submit_adoption'),
    path('update-payment-status/', views.update_payment_status, name='update_payment_status'),
    path('delete-adopter/<str:adopter_id>/', views.delete_adopter_view, name='delete_adopter'),
]
