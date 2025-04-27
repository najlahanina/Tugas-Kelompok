from django.urls import path
from .views import AnimalListView, AnimalCreateView, AnimalUpdateView, AnimalDeleteView
from django.urls import path

app_name = 'animals'

urlpatterns = [
    path('', AnimalListView.as_view(), name='animal_list'),
    path('add/', AnimalCreateView.as_view(), name='animal_add'),
    path('<int:pk>/edit/', AnimalUpdateView.as_view(), name='animal_edit'),
    path('<int:pk>/delete/', AnimalDeleteView.as_view(), name='animal_delete'),
]
