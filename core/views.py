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

class CursoListView(LoginRequiredMixin,ListView):
    model = Curso
    template_name = 'core/cursos/curso_list.html'
    context_object_name = 'cursos'

class CursoDetailView(LoginRequiredMixin,DetailView):
    model = Curso
    template_name = 'core/cursos/curso_detail.html'
    context_object_name = 'curso'

class CursoCreateView(LoginRequiredMixin,CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'core/cursos/curso_form.html'
    success_url = reverse_lazy('curso_list')

class CursoUpdateView(LoginRequiredMixin,UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'core/cursos/curso_form.html'
    success_url = reverse_lazy('curso_list')

class CursoDeleteView(LoginRequiredMixin,DeleteView):
    model = Curso
    template_name = 'core/cursos/curso_confirm_delete.html'
    success_url = reverse_lazy('curso_list')

# Vistas para capacitacion
class CapacitacionListView(LoginRequiredMixin,ListView):
    model = Capacitacion
    template_name = 'core/capacitacion/capacitacion_list.html'
    context_object_name = 'capacitaciones'

class CapacitacionCreateView(LoginRequiredMixin,CreateView):
    model = Capacitacion
    form_class = CapacitacionForm  # Usa el formulario CapacitacionForm
    template_name = 'core/capacitacion/capacitacion_form.html'

class CapacitacionUpdateView(LoginRequiredMixin,UpdateView):
    model = Capacitacion
    form_class = CapacitacionForm  # Usa el formulario CapacitacionForm
    template_name = 'core/capacitacion/capacitacion_form.html'

class CapacitacionDetailView(LoginRequiredMixin,DetailView):
    model = Capacitacion
    template_name = 'core/capacitacion/capacitacion_detail.html'

class CapacitacionDeleteView(LoginRequiredMixin,DeleteView):
    model = Capacitacion
    template_name = 'core/capacitacion/capacitacion_confirm_delete.html'
    success_url = reverse_lazy('capacitacion_list')

class CapacitacionFotoView(LoginRequiredMixin,FormView):
    template_name = "core/capacitacion/capacitacion_foto_form.html"
    form_class = CapacitacionFotoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion_id = self.kwargs.get('capacitacion_id')
        context['capacitacion'] = get_object_or_404(Capacitacion, id=capacitacion_id)
        context['fotos'] = CapacitacionFoto.objects.filter(
            capacitacion_id=capacitacion_id).order_by('-id')
        return context

    def form_valid(self, form):
        capacitacion_id = self.kwargs.get('capacitacion_id')
        capacitacion = get_object_or_404(Capacitacion, id=capacitacion_id)

        # Procesar el dato base64 enviado en el campo 'foto'
        foto_data = self.request.POST.get('foto')
        if foto_data:
            # Decodificar y guardar la imagen
            format, imgstr = foto_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{capacitacion_id}/capacitacion_foto.{ext}"
            photo = ContentFile(base64.b64decode(imgstr), name=file_name)

            # Crear una instancia de CapacitacionFoto
            CapacitacionFoto.objects.create(
                capacitacion=capacitacion,
                foto=photo
            )

        return redirect('capacitacion_foto', capacitacion_id=capacitacion_id)

    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al intentar guardar la foto.")
        return super().form_invalid(form)

def capacitacion_delete_foto(request, capacitacion_id, foto_id):
    if request.method == "POST":
        # Obtener la foto del objeto
        foto = get_object_or_404(CapacitacionFoto, id=foto_id, capacitacion_id=capacitacion_id)
        
        # Eliminar el archivo asociado a la foto
        if foto.foto:
            foto.foto.delete()  # Elimina el archivo de la ubicación de almacenamiento

        # Eliminar el registro de la base de datos
        foto.delete()

        # Redirigir de vuelta al template con las fotos actualizadas
        return redirect(reverse('capacitacion_foto', kwargs={'capacitacion_id': capacitacion_id}))

    return JsonResponse({"error": "Método no permitido."}, status=405)

class CapacitacionFotosView(LoginRequiredMixin,FormView):
    template_name = "core/capacitacion/capacitacion_foto_reporte.html"
    form_class = CapacitacionFotoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion_id = self.kwargs.get('capacitacion_id')
        context['capacitacion'] = get_object_or_404(Capacitacion, id=capacitacion_id)
        context['fotos'] = CapacitacionFoto.objects.filter(
            capacitacion_id=capacitacion_id).order_by('-id')
        return context
    
    def get_success_url(self):
        capacitacion_id = self.kwargs.get('capacitacion_id')
        # Aquí usamos reverse_lazy para obtener la URL de redirección
        return reverse_lazy('capacitacion_fotos', kwargs={'capacitacion_id': capacitacion_id})

def capacitacion_considera_foto(request, capacitacion_id, foto_id):
    if request.method == "POST":
        # Obtener la foto del objeto
        foto = get_object_or_404(CapacitacionFoto, id=foto_id, capacitacion_id=capacitacion_id)
        
        # Cambiar el valor de 'activar_para_reporte'
        foto.activar_para_reporte = not foto.activar_para_reporte
        foto.save()
        
        # Redirigir de vuelta a la vista 'capacitacion_fotos' usando reverse
        return redirect(reverse('capacitacion_fotos', kwargs={'capacitacion_id': capacitacion_id}))

    return JsonResponse({"error": "Método no permitido."}, status=405)

class CapacitacionPDF(LoginRequiredMixin,View):
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
        capacitacion_id = self.kwargs['capacitacion_id']
        capacitacion = get_object_or_404(Capacitacion, id=capacitacion_id)
        asistentes = Asistente.objects.filter(capacitacion=capacitacion)
        template_informe = 'core/reportes/informePDF.html'
        context = {
            'capacitacion':capacitacion,
            'asistentes':asistentes,
        }
        context['fotos'] = CapacitacionFoto.objects.filter(
            capacitacion_id=capacitacion_id).order_by('-id')
        response = HttpResponse(content_type='application/pdf')
        filename = f"{capacitacion.curso.nombre.replace(' ','-')}_{capacitacion.id}.pdf"
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
            error_message = "No se puede eliminar este instructor porque está asociado a una o más capacitaciones."
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
        self.capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        return Asistente.objects.filter(capacitacion=self.capacitacion)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['capacitacion'] = self.capacitacion
        return context

class AsistenteCreateView(LoginRequiredMixin,CreateView):
    model = Asistente
    form_class = AsistenteForm  # Usa el formulario AsistenteForm
    template_name = 'core/asistentes/asistente_form.html'

    def form_valid(self, form):
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        form.instance.capacitacion = capacitacion
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        context['id_capacitacion'] = capacitacion.id
        context['nombre'] = capacitacion.curso.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'capacitacion_id': self.kwargs['capacitacion_id']})

class AsistenteUpdateView(LoginRequiredMixin,UpdateView):
    model = Asistente
    form_class = AsistenteForm  # Usa el formulario AsistenteForm
    template_name = 'core/asistentes/asistente_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['capacitacion'] = capacitacion
        context['id_capacitacion'] = capacitacion.id
        context['nombre'] = capacitacion.curso.nombre
        context['numero'] = asistente.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'capacitacion_id': self.kwargs['capacitacion_id']})


class AsistenteDetailView(LoginRequiredMixin,DetailView):
    model = Asistente
    template_name = 'core/asistentes/asistente_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['capacitacion'] = capacitacion
        context['id_capacitacion'] = capacitacion.id
        context['nombre'] = capacitacion.curso.nombre
        context['numero'] = asistente.nombre
        return context

class AsistenteDeleteView(LoginRequiredMixin,DeleteView):
    model = Asistente
    template_name = 'core/asistentes/asistente_confirm_delete.html'
    success_url = reverse_lazy('asistente_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['capacitacion_id'])
        asistente = get_object_or_404(Asistente, id=self.kwargs['pk'])
        context['capacitacion'] = capacitacion
        context['id_capacitacion'] = capacitacion.id
        context['nombre'] = capacitacion.curso.nombre
        context['numero'] = asistente.nombre
        return context

    def get_success_url(self):
        return reverse_lazy('asistente_list', kwargs={'capacitacion_id': self.kwargs['capacitacion_id']})

class EnviarQRView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        # Obtener la capacitación por pk
        capacitacion = get_object_or_404(Capacitacion, pk=kwargs['pk'])

        # Crear el formulario
        form = CorreoForm(initial={
#            'destinatario': capacitacion.empresa.correo,
            'destinatario': 'evallardy@gmail.com',
            'asunto': f'QR para registro de la Capacitación {capacitacion.curso.nombre}',
            'contenido': f'Este correo contiene el QR para registro de la capacitación "{capacitacion.curso.nombre}".',
        })

        # Genera el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f'https//descapa.iagmexico.com/core/asistentes/registrar/{capacitacion.pk}/'  # URL de la capacitación
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
            'capacitacion': capacitacion,
            'qr_url': img_url
        })

    def post(self, request, *args, **kwargs):
        # Obtener la capacitación por pk
        capacitacion = get_object_or_404(Capacitacion, pk=kwargs['pk'])
        
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
            qr_data = f'https//descapa.iagmaxico.com/core/asistentes/registrar/{capacitacion.pk}/'  # URL de la capacitación
#            qr_data = f'//localhost:8000/core/asistentes/registrar/{capacitacion.pk}/'  # URL de la capacitación
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
#            email.attach(
#                f"qr_capacitacion_{capacitacion.pk}.png",  # Nombre del archivo
#                img_io.getvalue(),  # Imagen en formato binario
#                "image/png"  # Tipo de contenido
#            )

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
                'capacitacion': capacitacion,
                'qr_url': img_url,
                'respuesta': respuesta,
            })
        
        # Si el formulario no es válido, volver a mostrar el formulario con errores
        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'capacitacion': capacitacion,
            'qr_url': img_url
        })

class AsistenteRegistroView(CreateView):
    model = Asistente
    form_class = AsistenteForm
    template_name = 'core/asistentes/asistente_registrar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = get_object_or_404(Capacitacion, pk=self.kwargs['capacitacion_id'])
        context['capacitacion'] = capacitacion
        grupo = Asistente.objects.filter(capacitacion_id=self.kwargs['capacitacion_id'], activo='SI')
        context['grupo'] = grupo
        return context

    def form_valid(self, form):
        capacitacion = get_object_or_404(Capacitacion, pk=self.kwargs['capacitacion_id'])
        form.instance.capacitacion = capacitacion
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('registro_exitoso')

def generar_qr(capacitacion):
    url = f"{settings.SITE_URL}/asistentes/registrar/{capacitacion.id}/"
    qr = qrcode.make(url)
    qr.save(f"qr_capacitacion_{capacitacion.id}.png")

# Vistas para Evaluación
class EvaluacionDetailView(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = 'core/evaluaciones/evaluacion_detail.html'
    context_object_name = 'evaluacion'

    def get_object(self):
        # Obtener el curso según el curso_id en la URL
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        
        # Buscar o crear la evaluación asociada al curso
        evaluacion, created = Evaluacion.objects.get_or_create(curso=curso)
        return evaluacion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluacion = get_object_or_404(Evaluacion, curso_id=self.kwargs['curso_id'])
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

        curso_id = self.object.evaluacion.curso.id

        return redirect('evaluacion_detail', curso_id=curso_id)

class PreguntaDeleteView(LoginRequiredMixin,DeleteView):
    model = Evaluacion_Pregunta
    template_name = 'evaluaciones/pregunta_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('evaluacion_detail', kwargs={'curso_id': self.object.evaluacion.curso.id})

class RespuestaCreateView(LoginRequiredMixin,CreateView):
    model = Evaluacion_Respuestas
    fields = ['evaluacion_pregunta', 'respuesta', 'correcta']

    def form_valid(self, form):
        form.save()
        return redirect('evaluacion_detail', curso_id=form.instance.evaluacion_pregunta.evaluacion.curso.id)

class RespuestaDeleteView(LoginRequiredMixin,DeleteView):
    model = Evaluacion_Respuestas
    fields = ['evaluacion_pregunta', 'respuesta', 'correcta']

    def get_success_url(self):
        return reverse_lazy('evaluacion_detail', kwargs={'curso_id': self.object.evaluacion_pregunta.evaluacion.curso.id})

class EvaluacionAsistenteView(LoginRequiredMixin,TemplateView):
    template_name = "core/evaluaciones/evaluacion_asistente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener asistentes del curso
        asistente = get_object_or_404(Asistente, pk=self.kwargs['asistente_id'])

        # Obtener la evaluación basada en el curso
        evaluacion = get_object_or_404(Evaluacion, curso_id=self.kwargs['curso_id'])
        
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
        evaluacion = get_object_or_404(Evaluacion, curso_id=kwargs['curso_id'])
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
        return redirect('resultado_evaluacion', curso_id=evaluacion.curso.id, asistente_id=kwargs['asistente_id'])

class ResultadoEvaluacionView(LoginRequiredMixin,View):
    def get(self, request, curso_id, asistente_id):
        evaluacion = get_object_or_404(Evaluacion, curso_id=curso_id)
        asistente = get_object_or_404(Asistente, pk=asistente_id)
        
        # Obtener la última evaluación del asistente
        respuesta_asistente = RespuestaAsistente.objects.filter(
            evaluacion=evaluacion,
            asistente=asistente
        ).order_by('-id').first()

        if not respuesta_asistente:
            return redirect('evaluacion_detail', curso_id=curso_id, asistente_id=asistente_id)

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