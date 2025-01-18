from django.db import models
from datetime import datetime, timedelta
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import math
import base64
from usuario.models import Usuario

from feriados.views import trae_dia_habil

class Instructor(models.Model):
    ACTIVO_CHOICES = [
        ('SI', 'SI'),
        ('NO', 'NO'),
    ]
    nombre = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='usuario_instructor', blank=True, null=True)
    estatus = models.CharField(max_length=2 ,choices=ACTIVO_CHOICES, default='SI')

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('instructor_list')

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    contacto = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('empresa_list')

class Tema(models.Model):
    DURACION_CHOICES = [
        ('Horas', 'Horas'),
        ('Días', 'Días'),
    ]
    nombre = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField()
    unidad_duracion = models.CharField(max_length=5, choices=DURACION_CHOICES, default='Horas')
    horas_diarias = models.PositiveIntegerField()
    temario = models.TextField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=[('Activo', 'Activo'), ('Cancelado', 'Cancelado')],
        default='Activo',
    )

    def __str__(self):
        return self.nombre

    def total_preguntas(self):
        """
        Devuelve el total de preguntas asociadas al tema a través de la evaluación.
        """
        if hasattr(self, 'evaluacion_curso'):  # Verifica si tiene evaluación asociada
            return self.evaluacion_curso.evaluacion_preguntas.count()
        return 'Ninguna'  # Si no tiene evaluación, retorna 0

class Curso(models.Model):
    DURACION_CHOICES = [
        ('Horas', 'Horas'),
        ('Días', 'Días'),
    ]
    ACTIVAR_EVALUACION_CHOICES = [
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('XX', 'XX'),
    ]
    tema = models.ForeignKey(Tema, on_delete=models.PROTECT, related_name='tema_curso')
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='empresa_curso', null=True, blank=True)
    duracion = models.PositiveIntegerField()
    unidad_duracion = models.CharField(max_length=5, choices=DURACION_CHOICES, default='Horas')
    inicio = models.DateTimeField()
    final = models.DateTimeField(blank=True, null=True)
    horas_diarias = models.PositiveIntegerField(default=0)
    direccion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT, related_name="instructor_curso")
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=[('En curso', 'En curso'), ('Terminado', 'Terminado')],
        default='En curso',
    )
    activar_evaluacion = models.CharField(max_length=2, choices=ACTIVAR_EVALUACION_CHOICES, default='NO')

    def clean(self):
        # Validar que el instructor no tenga dos cursos al mismo tiempo
        if self.unidad_duracion == 'Días':
            fecha_inicial = self.inicio.replace(hour=0, minute=0, second=1)
#            inicio2 = trae_dia_habil(fecha_inicial, self.duracion - 1)
#            fecha_final = inicio2.replace(hour=23, minute=59, second=59)
        else:
            fecha_inicial = self.inicio
        fecha_final = self.fecha_termino()
        cursos = Curso.objects.filter(
            instructor=self.instructor).exclude(pk=self.pk).filter(
                Q(inicio__range=(fecha_inicial, fecha_final)) |
                Q(final__range=(fecha_inicial, fecha_final))
            )
        if cursos.exists():
            raise ValidationError(_('El instructor ya tiene un curso programado en esta fecha.'))

    def __str__(self):
        return self.tema.nombre

    def get_absolute_url(self):
        return reverse('curso_list')

    def fecha_termino(self):
        if self.unidad_duracion == 'Días':
            fecha_inicial = self.inicio.replace(hour=0, minute=0, second=1)
            inicio2 = trae_dia_habil(fecha_inicial, self.duracion - 1)
            fecha_final = inicio2.replace(hour=23, minute=59, second=59)
        else:
            if self.duracion > 0 and self.horas_diarias > 0 and self.duracion >= self.horas_diarias:
                resultado = self.duracion / self.horas_diarias
                dias_totales = math.ceil(resultado)

                fecha_final = trae_dia_habil(self.inicio, dias_totales - 1)  + timedelta(hours=self.horas_diarias)
            else:
                raise ValidationError(_('Las horas diarias o la duración esta incorrecto.'))
        return fecha_final

    def save(self, *args, **kwargs):
        self.full_clean()
        self.final = self.fecha_termino()
        super().save(*args, **kwargs)

    def total_preguntas(self):
        return self.tema.total_preguntas()

class CursoFoto(models.Model):
    FOTO_ACTIVAR_CHOICES = [
        ('SI', True),
        ('NO', False),
    ]
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='curso_foto')
    foto = models.ImageField("Foto", upload_to='Curso/', null=True, blank=True)
    activar_para_reporte = models.BooleanField(choices=FOTO_ACTIVAR_CHOICES, default=True)

class Asistente(models.Model):
    ASISTENTE_ACTIVO = [
        ('SI', 'SI'),
        ('NO', 'NO'),
    ]
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="asistentes")
    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)
    correo = models.EmailField()
    fecha_nacimiento = models.DateField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    activo = models.CharField(max_length=2, choices=ASISTENTE_ACTIVO, default='SI')

    def __str__(self):
        return f"{self.nombre} - {self.curso.nombre}"

    def get_absolute_url(self):
        return reverse('asistente_list')

    def calificaciones(self):
        respuestas = RespuestaAsistente.objects.filter(asistente=self)
        data = ''
        coma = ''
        for respuesta in respuestas:
            data += coma + str(respuesta.correctas)
            coma = ', '
        return data

class Evaluacion(models.Model):
    tema = models.OneToOneField(
        Tema, 
        on_delete=models.CASCADE, 
        related_name="evaluacion_curso",
        blank=True, 
        null=True
    )
    comentarios = models.TextField()

    def __str__(self):
        return f"Evaluación de {self.tema.nombre}"
        
class Evaluacion_Pregunta(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="evaluacion_preguntas")
    pregunta = models.TextField()

    def __str__(self):
        return f"Pregunta {self.pregunta}"

class Evaluacion_Respuestas(models.Model):
    evaluacion_pregunta = models.ForeignKey(Evaluacion_Pregunta, on_delete=models.CASCADE, related_name="evaluacion_respuestas")
    respuesta = models.TextField()
    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"Respuesta {self.respuesta}"

class Evaluacion_Asistente(models.Model):
    asistente = models.ForeignKey(Asistente, on_delete=models.PROTECT, related_name="evaluacion_asistente")
    comentarios = models.TextField()
    puntuacion = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        return f"Calificación asistente {self.puntuacion}"

class RespuestaAsistente(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="respuestas_asistentes")
    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE, related_name="respuestas_asistente")
    respuestas = models.JSONField()  # Almacena las respuestas en formato JSON
    correctas = models.IntegerField(default=0)  # Cantidad de respuestas correctas
    incorrectas = models.IntegerField(default=0)  # Cantidad de respuestas incorrectas
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuestas de {self.asistente} para {self.evaluacion.tema.nombre}"
