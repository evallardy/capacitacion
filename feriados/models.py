from django.db import models

class DiaFestivo(models.Model):
    fecha = models.DateField(unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['-fecha',]

    def __str__(self):
        return f"{self.nombre} ({self.fecha})"
