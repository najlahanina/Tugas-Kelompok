from django.urls import path
from . import views

app_name = 'attractions'
urlpatterns = [
    path('atraksi/', views.list_atraksi, name='list_atraksi'),
    path('atraksi/tambah/', views.tambah_atraksi, name='tambah_atraksi'),
    path('atraksi/edit/<int:index>/', views.edit_atraksi, name='edit_atraksi'),
    path('atraksi/hapus/<int:index>/', views.hapus_atraksi, name='hapus_atraksi'),

    path('wahana/', views.list_wahana, name='list_wahana'),
    path('wahana/tambah/', views.tambah_wahana, name='tambah_wahana'),
    path('wahana/edit/<int:index>/', views.edit_wahana, name='edit_wahana'),
    path('wahana/hapus/<int:index>/', views.hapus_wahana, name='hapus_wahana'),
]
