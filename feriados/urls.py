from django.urls import path
from .views import (
    DiaFestivoListView, DiaFestivoCreateView, DiaFestivoUpdateView, 
    DiaFestivoDeleteView, cargar_dias_festivos
    )

urlpatterns = [
    path('', DiaFestivoListView.as_view(), name='diafestivo_list'),
    path('nuevo/', DiaFestivoCreateView.as_view(), name='diafestivo_create'),
    path('<int:pk>/editar/', DiaFestivoUpdateView.as_view(), name='diafestivo_edit'),
    path('<int:pk>/eliminar/', DiaFestivoDeleteView.as_view(), name='diafestivo_delete'),
    path('cargar_dias_festivos', cargar_dias_festivos, name='cargar_dias_festivos'),
]
