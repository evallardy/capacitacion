from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):  
    materno = models.CharField("Materno", max_length=70, blank=True, null=True)
    created = models.DateTimeField("Creado", auto_now_add=True)
    modified = models.DateTimeField("Actualizado", auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'materno', 'first_name']
        db_table = 'Usuario'

    def __str__(self):
        return '%s' % (self.username)

    def nombre_completo(self):
        nombre_completo = self.first_name or ""
        if self.last_name:
            nombre_completo += f" {self.last_name}"
        return nombre_completo.strip()