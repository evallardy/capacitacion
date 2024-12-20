from django import forms
from .models import Curso, Capacitacion, Instructor, Empresa, Asistente, Evaluacion, CapacitacionFoto

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'costo', 'duracion', 'unidad_duracion', 'horas_diarias', 'estado', 'temario', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'unidad_duracion': forms.Select(attrs={'class': 'form-control'}),
            'horas_diarias': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'temario': forms.Textarea(attrs={'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'notas': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CapacitacionForm(forms.ModelForm):
    class Meta:
        model = Capacitacion
        fields = ['empresa', 'curso', 'instructor', 'duracion', 'unidad_duracion', 'horas_diarias',  
                    'inicio', 'direccion', 'costo', 'notas', 'estado', 'activar_evaluacion',
                    ]
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_duracion': forms.Select(attrs={'class': 'form-control'}),
            'inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructor': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'horas_diarias': forms.NumberInput(attrs={'class': 'form-control'}),
            'activar_evaluacion': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'empresa': 'Empresa:',
            'curso': 'Curso:',
            'instructor': 'Instructor:',
            'unidad_duracion': 'Unidad:',
            'duracion': 'Duración:',
            'horas_diarias': 'diarias:',
            'inicio': 'Inicio:',
            'direccion': 'Dirección:',
            'costo': 'Costo:',
            'notas': 'Notas:',
            'estado': 'Estado:',
            'activar_evaluacion': 'Act.eval.:',
        }
class CapacitacionFotoForm(forms.ModelForm):
    class Meta:
        model = CapacitacionFoto
        fields = ['foto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['nombre', 'celular', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'direccion', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AsistenteForm(forms.ModelForm):
    class Meta:
        model = Asistente
        fields = ['nombre', 'area', 'celular', 'correo']
        widgets = {
#            'capacitacion': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
#            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#            'qr_code': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class CorreoForm(forms.Form):
    destinatario = forms.EmailField(
        required=True,
        label="Correo electrónico del destinatario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el correo del destinatario'})
    )
    asunto = forms.CharField(
        max_length=200,
        label='Asunto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe el asunto del correo'})
    )
    contenido = forms.CharField(
        label='Contenido del Correo',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe el contenido del correo'})
    )

class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ['comentarios']
        widgets = {
            'comentarios': forms.Textarea(attrs={'class': 'form-control'}),
        }
