from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # User URLs
    path('', views.tambah_reservasi, name='tambah_reservasi'),
    path('<str:username_p>/<str:nama_atraksi>/<str:tanggal_kunjungan>/', views.detail_reservasi, name='detail_reservasi'),
    path('<str:username_p>/<str:nama_atraksi>/<str:tanggal_kunjungan>/edit/', views.edit_reservasi, name='edit_reservasi'),
    path('<str:username_p>/<str:nama_atraksi>/<str:tanggal_kunjungan>/batalkan/', views.batalkan_reservasi, name='batalkan_reservasi'),
    
    # Admin URLs
    path('admin/', views.admin_list_reservasi, name='admin_list_reservasi'),
    path('admin/<str:username_p>/<str:nama_atraksi>/<str:tanggal_kunjungan>/edit/', views.admin_edit_reservasi, name='admin_edit_reservasi'),
    path('admin/<str:username_p>/<str:nama_atraksi>/<str:tanggal_kunjungan>/batalkan/', views.admin_batalkan_reservasi, name='admin_batalkan_reservasi'),
]