from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View, TemplateView, FormView
import qrcode
import os
from django.template.loader import get_template
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import random
from django.http import JsonResponse
import json
from xhtml2pdf import pisa
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import *
from .forms import *

def index(request):
    template_name = 'core/index.html'
    return render(request, template_name)

class TemaListView(LoginRequiredMixin,ListView):
    model = Tema
    template_name = 'core/temas/tema_list.html'
    context_object_name = 'temas'

class TemaDetailView(LoginRequiredMixin,DetailView):
    model = Tema
    template_name = 'core/temas/tema_detail.html'
    context_object_name = 'tema'

class TemaCreateView(LoginRequiredMixin,CreateView):
    model = Tema
    form_class = TemaForm
    template_name = 'core/temas/tema_form.html'
    success_url = reverse_lazy('tema_list')

class TemaUpdateView(LoginRequiredMixin,UpdateView):
    model = Tema
    form_class = TemaForm
    template_name = 'core/temas/tema_form.html'
    success_url = reverse_lazy('tema_list')

class TemaDeleteView(LoginRequiredMixin,DeleteView):
    model = Tema
    template_name = 'core/temas/tema_confirm_delete.html'
    success_url = reverse_lazy('tema_list')

# Vistas para curso
class CursoListView(LoginRequiredMixin,ListView):
    model = Curso
    template_name = 'core/curso/curso_list.html'
    context_object_name = 'cursos'

class CursoCreateView(LoginRequiredMixin,CreateView):
    model = Curso
    form_class = CursoForm  # Usa el formulario CursoForm
    template_name = 'core/curso/curso_form.html'

class CursoUpdateView(LoginRequiredMixin,UpdateView):
    model = Curso
    form_class = CursoForm  # Usa el formulario CursoForm
    template_name = 'core/curso/curso_form.html'

class CursoDetailView(LoginRequiredMixin,DetailView):
    model = Curso
    template_name = 'core/curso/curso_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'instructor' in self.kwargs:
            context['instructor'] = self.kwargs['instructor']
        pk = self.kwargs['pk']
        curso = Curso.objects.filter(id=pk).first()
        context['nombre'] = curso.instructor.nombre
        return context


class CursoDeleteView(LoginRequiredMixin,DeleteView):
    model = Curso
    template_name = 'core/curso/curso_confirm_delete.html'
    success_url = reverse_lazy('curso_list')

class CursoFotoView(LoginRequiredMixin,FormView):
    template_name = "core/curso/curso_foto_form.html"
    form_class = CursoFotoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'instructor' in self.kwargs:
            context['instructor'] = self.kwargs['instructor']
        curso_id = self.kwargs.get('curso_id')
        context['curso'] = get_object_or_404(Curso, id=curso_id)
        context['fotos'] = CursoFoto.objects.filter(
            curso_id=curso_id).order_by('-id')
        return context

    def form_valid(self, form):
        curso_id = self.kwargs.get('curso_id')
        curso = get_object_or_404(Curso, id=curso_id)

        # Procesar el dato base64 enviado en el campo 'foto'
        foto_data = self.request.POST.get('foto')
        if foto_data:
            # Decodificar y guardar la imagen
            format, imgstr = foto_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{curso_id}/curso_foto.{ext}"
            photo = ContentFile(base64.b64decode(imgstr), name=file_name)

            # Crear una instancia de CursoFoto
            CursoFoto.objects.create(
                curso=curso,
                foto=photo
            )

        return redirect('curso_foto', curso_id=curso_id)

    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al intentar guardar la foto.")
        return super().form_invalid(form)

def curso_delete_foto(request, curso_id, foto_id):
    if request.method == "POST":
        # Obtener la foto del objeto
        foto = get_object_or_404(CursoFoto, id=foto_id, curso_id=curso_id)
        
        # Eliminar el archivo asociado a la foto
        if foto.foto:
            foto.foto.delete()  # Elimina el archivo de la ubicación de almacenamiento

        # Eliminar el registro de la base de datos
        foto.delete()

        # Redirigir de vuelta al template con las fotos actualizadas
        return redirect(reverse('curso_foto', kwargs={'curso_id': curso_id}))

    return JsonResponse({"error": "Método no permitido."}, status=405)

class CursoFotosView(LoginRequiredMixin,FormView):
    template_name = "core/curso/curso_foto_reporte.html"
    form_class = CursoFotoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso_id = self.kwargs.get('curso_id')
        context['curso'] = get_object_or_404(Curso, id=curso_id)
        context['fotos'] = CursoFoto.objects.filter(
            curso_id=curso_id).order_by('-id')
        return context
    
    def get_success_url(self):
        curso_id = self.kwargs.get('curso_id')
        # Aquí usamos reverse_lazy para obtener la URL de redirección
        return reverse_lazy('curso_fotos', kwargs={'curso_id': curso_id})

def curso_considera_foto(request, curso_id, foto_id):
    if request.method == "POST":
        # Obtener la foto del objeto
        foto = get_object_or_404(CursoFoto, id=foto_id, curso_id=curso_id)
        
        # Cambiar el valor de 'activar_para_reporte'
        foto.activar_para_reporte = not foto.activar_para_reporte
        foto.save()
        
        # Redirigir de vuelta a la vista 'ccurso_fotos' usando reverse
        return redirect(reverse('cursofotos', kwargs={'curso_id': curso_id}))

    return JsonResponse({"error": "Método no permitido."}, status=405)

class CursoPDF(LoginRequiredMixin,View):
    def link_callback(self, uri, rel):
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
            path = path.replace('\\static/', '\\core/static/')
            path = path.replace('/', '\\')
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path
    def get(self, request, *args, **kwargs):
        curso_id = self.kwargs['curso_id']
        curso = get_object_or_404(Curso, id=curso_id)
        asistentes = Asistente.objects.filter(curso=curso)
        template_informe = 'core/reportes/informePDF.html'
        context = {
            'curso':curso,
            'asistentes':asistentes,
        }
        context['fotos'] = CursoFoto.objects.filter(
            curso_id=curso_id).order_by('-id')
        response = HttpResponse(content_type='application/pdf')
        filename = f"{curso.tema.nombre.replace(' ','-')}_{curso.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        template = get_template(template_informe)
        html = template.render(context)
        pisaStatus = pisa.CreatePDF(
            html, 
            dest=response,
            link_callback=self.link_callback,
        )
        if pisaStatus.err:
            return HttpResponse('Error')
        return response

# Vistas para Instructor
class InstructorListView(LoginRequiredMixin,ListView):
    model = Instructor
    template_name = 'core/instructores/instructor_list.html'
    context_object_name = 'instructores'

class InstructorCreateView(LoginRequiredMixin,CreateView):
    model = Instructor
    form_class = InstructorForm  # Usa el formulario InstructorForm
    template_name = 'core/instructores/instructor_form.html'

class InstructorUpdateView(LoginRequiredMixin,UpdateView):
    model = Instructor
    form_class = InstructorForm  # Usa el formulario InstructorForm
    template_name = 'core/instructores/instructor_form.html'

class InstructorDetailView(LoginRequiredMixin,DetailView):
    model = Instructor
    template_name = 'core/instructores/instructor_detail.html'

class InstructorDeleteView(LoginRequiredMixin,DeleteView):
    model = Instructor
    template_name = 'core/instructores/instructor_confirm_delete.html'
    success_url = reverse_lazy('instructor_list')  # Cambia esto a la URL que redirige después de la eliminación

    def delete(self, request, *args, **kwargs):
        try:
            # Intentamos eliminar el objeto
            return super().delete(request, *args, **kwargs)
        except ProtectedError:
            # Capturamos el error y lo mostramos en una página de error
            error_message = "No se puede eliminar este instructor porque está asociado a una o más cursos."
            return render(request, 'instructor_error.html', {'error_message': error_message})

# Vistas para Empresa
class EmpresaListView(LoginRequiredMixin,ListView):
    model = Empresa
    template_name = 'core/empresas/empresa_list.html'
    context_object_name = 'empresas'

class EmpresaCreateView(LoginRequiredMixin,CreateView):
    model = Empresa
    form_class = EmpresaForm  # Usa el formulario EmpresaForm
    template_name = 'core/empresas/empresa_form.html'

class EmpresaUpdateView(LoginRequiredMixin,UpdateView):
    model = Empresa
    form_class = EmpresaForm  # Usa el formulario EmpresaForm
    template_name = 'core/empresas/empresa_form.html'

class EmpresaDetailView(LoginRequiredMixin,DetailView):
    model = Empresa
    template_name = 'core/empresas/empresa_detail.html'

class EmpresaDeleteView(LoginRequiredMixin,DeleteView):
    model = Empresa
    template_name = 'core/empresas/empresa_confirm_delete.html'
    success_url = reverse_lazy('empresa_list')

# Vistas para Asistente
class AsistenteListView(LoginRequiredMixin,ListView):
    model = Asistente
    template_name = 'core/asistentes/asistente_list.html'
    context_object_name = 'asistentes'

    def get_queryset(self):
        self.curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        return Asistente.objects.filter(curso=self.curso)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = self.curso
        return context

class AsistenteCreateView(LoginRequiredMixin,CreateView):
    model = Asistente
    form_class = AsistenteForm  # Usa el formulario AsistenteForm
    template_name = 'core/asistentes/asistente_form.html'

    def form_valid(self, form):
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        form.instance.curso = curso
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        context['curso_id'] = curso.id
        context['nombre'] = curso.tema.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'curso_id': self.kwargs['curso_id']})

class AsistenteUpdateView(LoginRequiredMixin,UpdateView):
    model = Asistente
    form_class = AsistenteForm  # Usa el formulario AsistenteForm
    template_name = 'core/asistentes/asistente_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['curso'] = curso
        context['curso_id'] = curso.id
        context['nombre'] = curso.tema.nombre
        context['numero'] = asistente.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'curso_id': self.kwargs['curso_id']})


class AsistenteDetailView(LoginRequiredMixin,DetailView):
    model = Asistente
    template_name = 'core/asistentes/asistente_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['curso'] = curso
        context['id_curso'] = curso.id
        context['nombre'] = curso.tema.nombre
        context['numero'] = asistente.nombre
        return context

class AsistenteDeleteView(LoginRequiredMixin,DeleteView):
    model = Asistente
    template_name = 'core/asistentes/asistente_confirm_delete.html'
    success_url = reverse_lazy('asistente_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['curso'] = curso
        context['curso_id'] = curso.id
        context['nombre'] = curso.tema.nombre
        context['numero'] = asistente.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'curso_id': self.kwargs['curso_id']})

class EnviarQRView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        # Obtener el curso por pk
        curso = get_object_or_404(Curso, pk=kwargs['pk'])

        # Crear el formulario
        form = CorreoForm(initial={
#            'destinatario': curso.empresa.correo,
            'destinatario': curso.empresa.correo,
            'asunto': f'QR para registro del curso {curso.tema.nombre}',
            'contenido': f'Este correo contiene el QR para registro del curso "{curso.tema.nombre}".',
        })

        # Genera el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f'https://descapa.iagmexico.com/core/asistentes/registrar/{curso.pk}/'  # URL del curso
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')

        # Guarda la imagen en un objeto BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Codifica la imagen a base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        img_url = f"data:image/png;base64,{img_base64}"

        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'curso': curso,
            'qr_url': img_url
        })

    def post(self, request, *args, **kwargs):
        # Obtener el curso por pk
        curso = get_object_or_404(Curso, pk=kwargs['pk'])
        
        # Crear el formulario con los datos enviados
        form = CorreoForm(request.POST)

        if form.is_valid():
            # Obtener los datos del formulario
            destinatario = form.cleaned_data['destinatario']
            asunto = form.cleaned_data['asunto']
            contenido = form.cleaned_data['contenido']

            # Generar el código QR nuevamente
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f'https://descapa.iagmexico.com/core/asistentes/registrar/{curso.pk}/'  # URL del curso
#            qr_data = f'//localhost:8000/core/asistentes/registrar/{curso.pk}/'  # URL del curso
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')

            # Guarda la imagen en un objeto BytesIO
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Codifica la imagen a base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            img_url = f"data:image/png;base64,{img_base64}"

            # Preparar el correo
            # from_email = settings.EMAIL_HOST_USER
            from_email = 'soporte@iagmexico.com'
            recipient_list = [destinatario]  # Usar el correo proporcionado por el usuario

            # Crear el mensaje del correo
            email = EmailMessage(
                asunto,  # Asunto
                contenido,  # Contenido
                from_email,  # De quien lo envia
                recipient_list,  # Destinatarios
            )

            # Adjuntar la imagen del QR al correo
            email.attach(
                f"qr_curso_{curso.pk}.png",  # Nombre del archivo
                img_io.getvalue(),  # Imagen en formato binario
                "image/png"  # Tipo de contenido
            )

            # Enviar el correo
            try:
                email.send()
#                messages.success(request, "Correo enviado correctamente.")
                respuesta = 'Correo enviado correctamente'
            except Exception as e:
#                messages.error(request, f"Error al enviar el correo: {str(e)}")
                respuesta = f"Error al enviar el correo: {str(e)}"

            # Redirigir a la página de éxito o mostrar mensaje
            return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
                'form': form,
                'curso': curso,
                'qr_url': img_url,
                'respuesta': respuesta,
            })
        
        # Si el formulario no es válido, volver a mostrar el formulario con errores
        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'curso': curso,
            'qr_url': img_url
        })

class AsistenteRegistroView(CreateView):
    model = Asistente
    form_class = AsistenteForm
    template_name = 'core/asistentes/asistente_registrar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso, pk=self.kwargs['curso_id'])
        context['curso'] = curso
        grupo = Asistente.objects.filter(curso_id=self.kwargs['curso_id'], activo='SI')
        context['grupo'] = grupo
        return context

    def form_valid(self, form):
        curso = get_object_or_404(Curso, pk=self.kwargs['curso_id'])
        form.instance.curso = curso
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('registro_exitoso')

def generar_qr(curso):
    url = f"{settings.SITE_URL}/asistentes/registrar/{curso.id}/"
    qr = qrcode.make(url)
    qr.save(f"qr_curso_{curso.id}.png")

# Vistas para Evaluación
class EvaluacionDetailView(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = 'core/evaluaciones/evaluacion_detail.html'
    context_object_name = 'evaluacion'

    def get_object(self):
        # Obtener el tema según el tema_id en la URL
        tema = get_object_or_404(Tema, id=self.kwargs['tema_id'])
        
        # Buscar o crear la evaluación asociada al tema
        evaluacion, created = Evaluacion.objects.get_or_create(tema=tema)
        return evaluacion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluacion = get_object_or_404(Evaluacion, tema_id=self.kwargs['tema_id'])
        context['evaluacion'] = evaluacion
        preguntas_respuestas = Evaluacion_Pregunta.objects.filter(evaluacion=evaluacion)
        context['preguntas_respuestas'] = preguntas_respuestas
        return context

class PreguntaCreateView(LoginRequiredMixin,CreateView):
    model = Evaluacion_Pregunta
    fields = ['evaluacion', 'pregunta']

    def form_valid(self, form):
        # Guardar la pregunta
        self.object = form.save()

        tema_id = self.object.evaluacion.tema.id

        return redirect('evaluacion_detail', tema_id=tema_id)

class PreguntaDeleteView(LoginRequiredMixin,DeleteView):
    model = Evaluacion_Pregunta
    template_name = 'evaluaciones/pregunta_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('evaluacion_detail', kwargs={'tema_id': self.object.evaluacion.tema.id})

class RespuestaCreateView(LoginRequiredMixin,CreateView):
    model = Evaluacion_Respuestas
    fields = ['evaluacion_pregunta', 'respuesta', 'correcta']

    def form_valid(self, form):
        form.save()
        return redirect('evaluacion_detail', tema_id=form.instance.evaluacion_pregunta.evaluacion.tema.id)

class RespuestaDeleteView(LoginRequiredMixin,DeleteView):
    model = Evaluacion_Respuestas
    fields = ['evaluacion_pregunta', 'respuesta', 'correcta']

    def get_success_url(self):
        return reverse_lazy('evaluacion_detail', kwargs={'tema_id': self.object.evaluacion_pregunta.evaluacion.tema.id})

class EvaluacionAsistenteView(LoginRequiredMixin,TemplateView):
    template_name = "core/evaluaciones/evaluacion_asistente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener asistentes del tema
        asistente = get_object_or_404(Asistente, pk=self.kwargs['asistente_id'])

        # Obtener la evaluación basada en el tema
        evaluacion = get_object_or_404(Evaluacion, tema_id=self.kwargs['tema_id'])
        
        # Barajar las preguntas y sus respuestas
        preguntas = list(evaluacion.evaluacion_preguntas.all())
        random.shuffle(preguntas)
        
        for pregunta in preguntas:
            respuestas = list(pregunta.evaluacion_respuestas.all())
            random.shuffle(respuestas)
            pregunta.respuestas_shuffled = respuestas

        context['asistente'] = asistente
        context['evaluacion'] = evaluacion
        context['preguntas'] = preguntas
        return context

class GuardarRespuestasView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        evaluacion = get_object_or_404(Evaluacion, tema_id=kwargs['tema_id'])
        asistente = get_object_or_404(Asistente, pk=kwargs['asistente_id'])
        respuestas_dict = {}
        correctas = 0
        incorrectas = 0

        # Procesar las respuestas enviadas
        for key, value in request.POST.items():
            if key.startswith('respuesta_'):
                pregunta_id = int(key.split('_')[1])
                respuesta_id = int(value)
                respuesta = get_object_or_404(Evaluacion_Respuestas, id=respuesta_id)

                # Validar si la respuesta es correcta
                if respuesta.correcta:
                    correctas += 1
                else:
                    incorrectas += 1

                # Almacenar la respuesta seleccionada en un diccionario
                respuestas_dict[pregunta_id] = {
                    "pregunta_id": pregunta_id,
                    "respuesta_id": respuesta.id,
                    "respuesta_texto": respuesta.respuesta,
                    "correcta": respuesta.correcta,
                }

        # Guardar las respuestas como JSON en RespuestaAsistente
        respuestas_json = json.dumps(respuestas_dict)
        RespuestaAsistente.objects.create(
            evaluacion=evaluacion,
            asistente=asistente,
            respuestas=respuestas_json,
            correctas=correctas,
            incorrectas=incorrectas
        )

#        return JsonResponse({"success": True, "correctas": correctas, "incorrectas": incorrectas})
        return redirect('resultado_evaluacion', tema_id=evaluacion.tema.id, asistente_id=kwargs['asistente_id'])

class ResultadoEvaluacionView(LoginRequiredMixin,View):
    def get(self, request, tema_id, asistente_id):
        evaluacion = get_object_or_404(Evaluacion, tema_id=tema_id)
        asistente = get_object_or_404(Asistente, pk=asistente_id)
        
        # Obtener la última evaluación del asistente
        respuesta_asistente = RespuestaAsistente.objects.filter(
            evaluacion=evaluacion,
            asistente=asistente
        ).order_by('-id').first()

        if not respuesta_asistente:
            return redirect('evaluacion_detail', tema_id=tema_id, asistente_id=asistente_id)

        contexto = {
            'evaluacion': evaluacion,
            'respuesta_asistente': respuesta_asistente,
            'asistente':asistente
        }
        return render(request, 'core/evaluaciones/resultado_evaluacion.html', contexto)

    def post(self, request, *args, **kwargs):
        # Obtener al asistente y marcarlo como inactivo
        asistente = get_object_or_404(Asistente, pk=kwargs['asistente_id'])
        
        # Actualizar el estado del asistente
        asistente.activo = 'NO'
        asistente.save()

        # Redirigir a la vista de despedida
        return redirect('despedida_evaluacion')

class DespedidaEvaluacionView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'core/evaluaciones/despedida.html')

# Vistas para actividades
class InstructorCursoListView(LoginRequiredMixin,ListView):
    model = Curso
    template_name = 'core/actividades/curso_instructor_list.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        usuario = Usuario.objects.filter(username=self.request.user.username).first()
        instructor = Instructor.objects.filter(usuario=usuario).first()
        return Curso.objects.filter(instructor=instructor)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.filter(username=self.request.user.username).first()
        instructor = Instructor.objects.filter(usuario=usuario).first()
        context['instructor'] = instructor
        return context

class InstructorAsistenteListView(LoginRequiredMixin,ListView):
    model = Asistente
    template_name = 'core/actividades/curso_asistente_list.html'
    context_object_name = 'asistentes'

    def get_queryset(self):
        self.curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        return Asistente.objects.filter(curso=self.curso)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = self.curso
        context['curso'] = curso
        return context

def activaEvaluacion(request, curso_id):
    template_name = 'core/actividades/curso_instructor_list.html'
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.activar_evaluacion == 'NO':
        curso.activar_evaluacion = 'SI'
    else:
        curso.activar_evaluacion = 'NO'
    curso.save()
    return redirect('instructor_curso_list')
    
def terminarCurso(request, curso_id):
    template_name = 'core/actividades/curso_instructor_list.html'
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.estado == 'Terminado':
        curso.estado = 'En curso'
    else:
        curso.estado = 'Terminado'
    curso.save()
    return redirect('instructor_curso_list')
