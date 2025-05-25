from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # User URLs
    path('', views.tambah_reservasi, name='tambah_reservasi'),
    path('<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/', views.detail_reservasi, name='detail_reservasi'),
    path('<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/edit/', views.edit_reservasi, name='edit_reservasi'),
    path('<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/batalkan/', views.batalkan_reservasi, name='batalkan_reservasi'),
    path('reservasi-wahana/', views.tambah_reservasi_wahana, name='tambah_reservasi_wahana'),
    path('reservasi-wahana/<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/detail/', 
         views.detail_reservasi_wahana, name='detail_reservasi_wahana'),
    path('reservasi-wahana/<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/edit/', 
         views.edit_reservasi_wahana, name='edit_reservasi_wahana'),
    path('reservasi-wahana/<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/batal/', 
         views.batalkan_reservasi_wahana, name='batalkan_reservasi_wahana'),
    path('list-reservasi/', views.list_reservasi, name='list_reservasi'),
    path('list-reservasi-tersedia/', views.list_reservasi_tersedia, name='list_reservasi_tersedia'),
    
    # Admin URLs
    path('admin/', views.admin_list_reservasi, name='admin_list_reservasi'),
    path('admin/<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/edit/', views.admin_edit_reservasi, name='admin_edit_reservasi'),
    path('admin/<str:username_p>/<str:nama_fasilitas>/<str:tanggal_kunjungan>/batalkan/', views.admin_batalkan_reservasi, name='admin_batalkan_reservasi'),
]