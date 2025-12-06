import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from django.conf import settings
from django.core.mail import send_mail
from django.http import BadHeaderError
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Destination, Cruise, DestinationReview, CruiseReview, Purchase
from .forms import DestinationReviewForm, CruiseReviewForm
from django.contrib.auth.forms import UserCreationForm
from .forms import DestinationReviewForm, CruiseReviewForm
from django.views.generic import DetailView

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
        return render(request,'about.html')

def destinations(request):
      all_destinations = models.Destination.objects.all()
      return render(request,'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destination_detail.html'
    context_object_name = 'destination'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.object
        user = self.request.user

        # Cruceros asociados
        context['cruises'] = destination.cruises.all()

        # Reviews existentes
        reviews = destination.reviews.all()
        context['reviews'] = reviews

        # Valoración media
        if reviews.exists():
            context['avg_rating'] = sum([r.rating for r in reviews]) / reviews.count()
        else:
            context['avg_rating'] = None

        # Formulario de review
        context['review_form'] = DestinationReviewForm()

        # Comprobar si el usuario ha comprado el destino
        if user.is_authenticated:
            has_purchased = Purchase.objects.filter(user=user, destination=destination).exists()
        else:
            has_purchased = False

        # Guardamos en el contexto
        context['has_purchased'] = has_purchased
        context['can_review'] = has_purchased  # solo puede dejar review si ha comprado

        return context

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

class CruiseDetailView(DetailView):
    model = Cruise
    template_name = 'cruise_detail.html'
    context_object_name = 'cruise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cruise = self.object
        user = self.request.user

        # Reviews existentes
        reviews = cruise.reviews.all()
        context['reviews'] = reviews

        # Valoración media
        if reviews.exists():
            context['avg_rating'] = sum([r.rating for r in reviews]) / reviews.count()
        else:
            context['avg_rating'] = None

        # Formulario de review
        context['review_form'] = CruiseReviewForm()  # Asegúrate de tener este formulario

        # Comprobar si el usuario ha comprado el crucero
        if user.is_authenticated:
            has_purchased = Purchase.objects.filter(user=user, cruise=cruise).exists()
        else:
            has_purchased = False

        context['has_purchased'] = has_purchased
        context['can_review'] = has_purchased  # solo puede dejar review si ha comprado

        return context

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
                

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User registered successfully! You can now log in.")
            return redirect('login')  # Redirige al login
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'login.html')

# LOGOUT
def logout_view(request):
    logout(request)              # Cierra la sesión
    return render(request, 'logout.html')

@login_required
def add_destination_review(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if not Purchase.objects.filter(user=request.user, destination=destination).exists():
        return redirect('destination_detail', pk=pk)

    if request.method == 'POST':
        form = DestinationReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.destination = destination
            review.save()
            return redirect('destination_detail', pk=pk)
    return redirect('destination_detail', pk=pk)


@login_required
def add_cruise_review(request, pk):
    cruise = get_object_or_404(Cruise, pk=pk)
    if not Purchase.objects.filter(user=request.user, cruise=cruise).exists():
        return redirect('cruise_detail', pk=pk)

    if request.method == 'POST':
        form = CruiseReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.cruise = cruise
            review.save()
            return redirect('cruise_detail', pk=pk)
    return redirect('cruise_detail', pk=pk)

@login_required
def buy_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    Purchase.objects.get_or_create(user=request.user, destination=destination)
    return redirect('destination_detail', pk=pk)

@login_required
def buy_cruise(request, pk):
    cruise = get_object_or_404(Cruise, pk=pk)
    Purchase.objects.get_or_create(user=request.user, cruise=cruise)
    return redirect('cruise_detail', pk=pk)