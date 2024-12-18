from django import forms
from .models import DiaFestivo

class DiaFestivoForm(forms.ModelForm):
    class Meta:
        model = DiaFestivo
        fields = ['fecha', 'nombre']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }