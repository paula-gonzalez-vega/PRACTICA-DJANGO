import logging
from django.shortcuts import render
from django.urls import reverse_lazy

from django.conf import settings
from django.core.mail import send_mail
from django.http import BadHeaderError
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from .models import Destination
from django.contrib import messages

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
        return render(request,'about.html')

def destinations(request):
      all_destinations = models.Destination.objects.all()
      return render(request,'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

class DestinationCreateView(generic.CreateView):
    template_name = 'destination_form.html'
    model = models.Destination
    # Añadimos el campo de la imagen
    fields = ['name', 'description', 'image']
    
class DestinationUpdateView(generic.UpdateView):
    template_name = 'destination_form.html'
    model = models.Destination
    fields = ['name', 'description', 'image']

class DestinationDeleteView(generic.DeleteView):
    template_name = 'destination_confirm_delete.html'
    model = models.Destination
    success_url = reverse_lazy('destinations')

class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

# Añadimos el logger para registrar errores de envío de correo
logger  = logging.getLogger(__name__)
class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'notes', 'cruise']
    success_url = reverse_lazy('index')
    success_message = "Thank you, %(name)s! We will email you when we have more information about %(cruise)s"

    # Enviamos un correo electrónico al crear una solicitud de información
    def form_valid(self, form):
        data = form.cleaned_data
        cruise = data.get('cruise')
        subject = "Información sobre " + str(cruise)
        message = "Hola " + data.get('name') + ",\n\nGracias por tu interés en " + str(cruise) + ". Te escribiremos pronto con más información. Tendremos en cuenta tus notas: " + data.get('notes') + "\n\nUn saludo,\nReleCloud Team"
        email_to = data.get('email')
        email_from = settings.EMAIL_HOST_USER

        try:
            send_mail(subject, message, email_from, [email_to], fail_silently=False)
        except (BadHeaderError, Exception) as e:
            logger.error(f"Error enviando email de InfoRequest: {e}")
            messages.error(self.request, "Se ha guardado tu solicitud, pero hubo un error enviando el email.")
        else:
            messages.success(self.request, "Se ha guardado tu solicitud y se ha enviado un email de confirmación.")

        return super().form_valid(form)
                