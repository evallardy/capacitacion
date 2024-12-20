from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import timedelta
import holidays
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import DiaFestivo
from .forms import *

class DiaFestivoListView(LoginRequiredMixin, ListView):
    model = DiaFestivo
    template_name = "feriados/diafestivo_list.html"
    context_object_name = "dias_festivos"

class DiaFestivoCreateView(LoginRequiredMixin, CreateView):
    model = DiaFestivo
    form_class = DiaFestivoForm
    template_name = "feriados/diafestivo_form.html"
    success_url = reverse_lazy('diafestivo_list')

class DiaFestivoUpdateView(LoginRequiredMixin, UpdateView):
    model = DiaFestivo
    form_class = DiaFestivoForm
    template_name = "feriados/diafestivo_form.html"
    success_url = reverse_lazy('diafestivo_list')

class DiaFestivoDeleteView(LoginRequiredMixin, DeleteView):
    model = DiaFestivo
    template_name = "feriados/diafestivo_confirm_delete.html"
    success_url = reverse_lazy('diafestivo_list')

import logging
logger = logging.getLogger(__name__)

def cargar_dias_festivos(request):
    try:
        mexican_holidays = holidays.Mexico(years=range(2024, 2031))
        for fecha, nombre in mexican_holidays.items():
            DiaFestivo.objects.get_or_create(fecha=fecha, nombre=nombre)
        logger.info("Días festivos procesados correctamente")
        return HttpResponse("Días festivos cargados")
    except Exception as e:
        logger.error(f"Error al procesar: {e}")
        return HttpResponse("Ocurrió un error", status=500)

def es_dia_habil(fecha):
    if fecha.weekday() in (5, 6) or DiaFestivo.objects.filter(fecha=fecha).exists():
        return False
    return True        

def trae_dia_habil(fecha, numero):
    if numero <= 0:
        return fecha
    else:
        dias_habiles = 0
        for dia in range(1,365):
            fecha_calculada = fecha + timedelta(days=dia)
            if es_dia_habil(fecha_calculada):
                dias_habiles += 1
                if dias_habiles == numero:
                    return fecha_calculada
                
        