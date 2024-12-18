from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput

from .models import Usuario

ACCESO = (
    (False, 'Sin acceso'),
    (True, 'Activo'),
)

class UsuarioForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo',
            'password1': 'Contraseña',
            'password2': 'Confirmación'
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = False
        self.fields['password2'].required = False

class UsuarioFormEdit(forms.ModelForm):
    is_active = forms.ChoiceField(
        choices=ACCESO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Activo'
    )
    password1 = forms.CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        label='Nueva Contraseña'
    )
    password2 = forms.CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        label='Confirmación Contraseña'
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'is_active', 'password1', 'password2']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo',
            'is_active': 'Activo',
            'password1': 'Contraseña',
            'password2': 'Confirmación'
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['is_active'].required = False

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
