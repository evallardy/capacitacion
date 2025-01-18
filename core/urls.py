from django.urls import path
from django.views.generic import TemplateView

from .views import *

# Configuración de URLs
urlpatterns = [
    # URLs para Temas
    path('tema/', TemaListView.as_view(), name='tema_list'),
    path('tema/<int:pk>/', TemaDetailView.as_view(), name='tema_detail'),
    path('tema/nuevo/', TemaCreateView.as_view(), name='tema_create'),
    path('tema/<int:pk>/editar/', TemaUpdateView.as_view(), name='tema_update'),
    path('tema/<int:pk>/eliminar/', TemaDeleteView.as_view(), name='tema_delete'),

    # URLs para Cursos
    path('curso/', CursoListView.as_view(), name='curso_list'),
    path('curso/nuevo/', CursoCreateView.as_view(), name='curso_create'),
    path('curso/<int:pk>/', CursoDetailView.as_view(), name='curso_detail'),
    path('curso/<int:pk>/<int:instructor>/', CursoDetailView.as_view(), name='curso_detail'),
    path('curso/<int:pk>/editar/', CursoUpdateView.as_view(), name='curso_update'),
    path('curso/<int:pk>/eliminar/', CursoDeleteView.as_view(), name='curso_delete'),
    path('curso/<int:curso_id>/foto/', CursoFotoView.as_view(), name='curso_foto'),
    path('curso/<int:curso_id>/foto/<int:foto_id>/eliminar/', curso_delete_foto, 
         name='eliminar_foto'),
    path('curso/<int:curso_id>/fotos/', CursoFotosView.as_view(), name='curso_fotos'),
    path('curso/<int:curso_id>/foto/<int:foto_id>/considerar/', curso_considera_foto, 
         name='considera_foto'),
    path('cursoPDF/<int:curso_id>/', CursoPDF.as_view(), name='cursoPDF'),

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
    path('asistentes/<int:curso_id>/', AsistenteListView.as_view(), name='asistente_list'),
    path('asistentes/<int:curso_id>/nuevo/', AsistenteCreateView.as_view(), name='asistente_create'),
    path('asistentes/<int:curso_id>/<int:pk>/', AsistenteDetailView.as_view(), name='asistente_detail'),
    path('asistentes/<int:curso_id>/<int:pk>/editar/', AsistenteUpdateView.as_view(), name='asistente_update'),
    path('asistentes/<int:curso_id>/<int:pk>/eliminar/', AsistenteDeleteView.as_view(), name='asistente_delete'),

    # Registro de Asistentes
    path('asistentes/registrar/<int:curso_id>/', AsistenteRegistroView.as_view(), name='registrar_asistente'),
    path('registro/exitoso/', TemplateView.as_view(template_name='core/asistentes/asistente_exitoso.html'), name='registro_exitoso'),
    path('enviar_qr/<int:pk>/', EnviarQRView.as_view(), name='enviar_qr'),

    # URLs para Evaluación
    path('evaluacion/tema/<int:tema_id>/', EvaluacionDetailView.as_view(), name='evaluacion_detail'),
    path('evaluacion/pregunta/create/', PreguntaCreateView.as_view(), name='pregunta_create'),
    path('evaluacion/pregunta/<int:pk>/delete/', PreguntaDeleteView.as_view(), name='pregunta_delete'),
    path('evaluacion/respuesta/create/', RespuestaCreateView.as_view(), name='respuesta_create'),
    path('evaluacion/respuesta/<int:pk>/delete/', RespuestaDeleteView.as_view(), name='respuesta_delete'),
    path('evaluacion/asistente/<int:tema_id>/<int:asistente_id>/', EvaluacionAsistenteView.as_view(), name='evaluacion_asistente'),
    path('evaluacion/guarda/<int:tema_id>/<int:asistente_id>/', GuardarRespuestasView.as_view(), name='guardar_respuestas'),
    path('evaluacion/resultado/<int:tema_id>/<int:asistente_id>/', ResultadoEvaluacionView.as_view(), name='resultado_evaluacion'),
    path('evaluacion/despedida/', DespedidaEvaluacionView.as_view(), name='despedida_evaluacion'),
    
    # URLs para Actividades
    path('actividades/instructor_curso/', InstructorCursoListView.as_view(), name='instructor_curso_list'),
    path('instructor/asistentes/<int:curso_id>/', InstructorAsistenteListView.as_view(), name='instructor_asistente_list'),
    path('curso/<int:curso_id>/foto/<int:instructor>/', CursoFotoView.as_view(), name='instructor_curso_foto'),
    path('actividades/activar_evaluacion/<int:curso_id>/', activaEvaluacion, name='activar_evaluacion'),
    path('actividades/terminar_curso/<int:curso_id>/', terminarCurso, name='terminar_curso'),
]
