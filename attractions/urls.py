from django.urls import path
from . import views

app_name = 'attractions'
urlpatterns = [
    path('atraksi/', views.list_atraksi, name='list_atraksi'),
    path('atraksi/tambah/', views.tambah_atraksi, name='tambah_atraksi'),
    path('atraksi/edit/<str:nama_atraksi>/', views.edit_atraksi, name='edit_atraksi'),
    path('atraksi/hapus/<str:nama_atraksi>/', views.hapus_atraksi, name='hapus_atraksi'),

    path('wahana/', views.list_wahana, name='list_wahana'),
    path('wahana/tambah/', views.tambah_wahana, name='tambah_wahana'),
    path('wahana/edit/<str:nama_wahana>/', views.edit_wahana, name='edit_wahana'),
    path('wahana/hapus/<str:nama_wahana>/', views.hapus_wahana, name='hapus_wahana'),

    path('atraksi-trainer/', views.list_atraksi_trainer, name='list_atraksi_trainer'),
    path('atraksi-trainer/tambah/', views.tambah_atraksi_trainer, name='tambah_atraksi_trainer'),
    path('atraksi-trainer/edit/<int:id>/', views.edit_atraksi_trainer, name='edit_atraksi_trainer'),
    path('atraksi-trainer/hapus/<int:id>/', views.hapus_atraksi_trainer, name='hapus_atraksi_trainer'),

]
