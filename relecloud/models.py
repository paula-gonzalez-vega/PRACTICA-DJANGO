from django.db import models
# Añadimos para poder usar reverse en get_absolute_url
from django.urls import reverse

# Modelo de destino
class Destination(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=50
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    # Añadimos un campo para la imagen 
    image= models.ImageField(
        upload_to='destinations/',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        # Traducimos un nombre de ruta a su URL correspondiente
        return reverse('destination_detail', kwargs={'pk': self.pk})


# Modelo de crucero
class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=50
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )

    def __str__(self):
        return self.name


# Modelo de solicitud de información
class InfoRequest(models.Model):
    name = models.CharField(
        null=False,
        blank=False,
        max_length=50
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )

