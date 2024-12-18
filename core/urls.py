from django.urls import path
from django.views.generic import TemplateView

from .views import *

# Configuración de URLs
urlpatterns = [
    # URLs para Cursos
    path('curso/', CursoListView.as_view(), name='curso_list'),
    path('curso/<int:pk>/', CursoDetailView.as_view(), name='curso_detail'),
    path('curso/nuevo/', CursoCreateView.as_view(), name='curso_create'),
    path('curso/<int:pk>/editar/', CursoUpdateView.as_view(), name='curso_update'),
    path('curso/<int:pk>/eliminar/', CursoDeleteView.as_view(), name='curso_delete'),

    # URLs para Capacitacion
    path('capacitacion/', CapacitacionListView.as_view(), name='capacitacion_list'),
    path('capacitacion/nuevo/', CapacitacionCreateView.as_view(), name='capacitacion_create'),
    path('capacitacion/<int:pk>/', CapacitacionDetailView.as_view(), name='capacitacion_detail'),
    path('capacitacion/<int:pk>/editar/', CapacitacionUpdateView.as_view(), name='capacitacion_update'),
    path('capacitacion/<int:pk>/eliminar/', CapacitacionDeleteView.as_view(), name='capacitacion_delete'),
    path('capacitacion/<int:capacitacion_id>/foto/', CapacitacionFotoView.as_view(), name='capacitacion_foto'),
    path('capacitacion/<int:capacitacion_id>/foto/<int:foto_id>/eliminar/', capacitacion_delete_foto, 
         name='eliminar_foto'),
    path('capacitacion/<int:capacitacion_id>/fotos/', CapacitacionFotosView.as_view(), name='capacitacion_fotos'),
    path('capacitacion/<int:capacitacion_id>/foto/<int:foto_id>/considerar/', capacitacion_considera_foto, 
         name='considera_foto'),
    path('capacitacionPDF/<int:capacitacion_id>/', CapacitacionPDF.as_view(), name='capacitacionPDF'),

    # URLs para Instructor
    path('instructores/', InstructorListView.as_view(), name='instructor_list'),
    path('instructores/nuevo/', InstructorCreateView.as_view(), name='instructor_create'),
    path('instructores/<int:pk>/', InstructorDetailView.as_view(), name='instructor_detail'),
    path('instructores/<int:pk>/editar/', InstructorUpdateView.as_view(), name='instructor_update'),
    path('instructores/<int:pk>/eliminar/', InstructorDeleteView.as_view(), name='instructor_delete'),

    # URLs para Empresa
    path('empresas/', EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/nuevo/', EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/', EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/editar/', EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresas/<int:pk>/eliminar/', EmpresaDeleteView.as_view(), name='empresa_delete'),

    # URLs para Asistente
    path('asistentes/<int:capacitacion_id>/', AsistenteListView.as_view(), name='asistente_list'),
    path('asistentes/<int:capacitacion_id>/nuevo/', AsistenteCreateView.as_view(), name='asistente_create'),
    path('asistentes/<int:capacitacion_id>/<int:pk>/', AsistenteDetailView.as_view(), name='asistente_detail'),
    path('asistentes/<int:capacitacion_id>/<int:pk>/editar/', AsistenteUpdateView.as_view(), name='asistente_update'),
    path('asistentes/<int:capacitacion_id>/<int:pk>/eliminar/', AsistenteDeleteView.as_view(), name='asistente_delete'),

    # Registro de Asistentes
    path('asistentes/registrar/<int:capacitacion_id>/', AsistenteRegistroView.as_view(), name='registrar_asistente'),
    path('registro/exitoso/', TemplateView.as_view(template_name='core/asistentes/asistente_exitoso.html'), name='registro_exitoso'),
    path('enviar_qr/<int:pk>/', EnviarQRView.as_view(), name='enviar_qr'),

    # URLs para Evaluación
    path('evaluacion/curso/<int:curso_id>/', EvaluacionDetailView.as_view(), name='evaluacion_detail'),
    path('evaluacion/pregunta/create/', PreguntaCreateView.as_view(), name='pregunta_create'),
    path('evaluacion/pregunta/<int:pk>/delete/', PreguntaDeleteView.as_view(), name='pregunta_delete'),
    path('evaluacion/respuesta/create/', RespuestaCreateView.as_view(), name='respuesta_create'),
    path('evaluacion/respuesta/<int:pk>/delete/', RespuestaDeleteView.as_view(), name='respuesta_delete'),
    path('evaluacion/asistente/<int:curso_id>/<int:asistente_id>/', EvaluacionAsistenteView.as_view(), name='evaluacion_asistente'),
    path('evaluacion/guarda/<int:curso_id>/<int:asistente_id>/', GuardarRespuestasView.as_view(), name='guardar_respuestas'),
    path('evaluacion/resultado/<int:curso_id>/<int:asistente_id>/', ResultadoEvaluacionView.as_view(), name='resultado_evaluacion'),
    path('evaluacion/despedida/', DespedidaEvaluacionView.as_view(), name='despedida_evaluacion'),
]
