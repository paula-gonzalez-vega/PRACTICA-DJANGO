from django.db import models
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

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
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

