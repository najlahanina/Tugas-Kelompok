from django.urls import path
from . import views

urlpatterns = [
    path('', views.feeding_list, name='feeding_list'),  # list + tombol tambah
    path('add/', views.add_feeding, name='add_feeding'),  # tambah
    path('edit/<int:feeding_id>/', views.edit_feeding, name='edit_feeding'),  # edit
    path('delete/<int:feeding_id>/', views.delete_feeding, name='delete_feeding'),  # hapus
    path('mark_as_done/<int:feeding_id>/', views.mark_as_done, name='mark_as_done'),  # beri pakan
]
