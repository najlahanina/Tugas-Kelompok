from django.urls import path
from .views import HabitatListView, HabitatDetailView, HabitatCreateView, HabitatUpdateView, HabitatDeleteView

app_name = 'habitats'

urlpatterns = [
    path('', HabitatListView.as_view(), name='habitat_list'),
    path('<int:pk>/', HabitatDetailView.as_view(), name='habitat_detail'),
    path('add/', HabitatCreateView.as_view(), name='habitat_add'),
    path('<int:pk>/edit/', HabitatUpdateView.as_view(), name='habitat_edit'),
    path('<int:pk>/delete/', HabitatDeleteView.as_view(), name='habitat_delete'),
]