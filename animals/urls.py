from django.urls import path
from .views import AnimalListView, AnimalCreateView, AnimalUpdateView, AnimalDeleteView

urlpatterns = [
    path('', AnimalListView.as_view(), name='animal-list'),
    path('add/', AnimalCreateView.as_view(), name='animal-add'),
    path('<int:pk>/edit/', AnimalUpdateView.as_view(), name='animal-edit'),
    path('<int:pk>/delete/', AnimalDeleteView.as_view(), name='animal-delete'),
]