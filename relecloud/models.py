from django.db import models
from django.urls import reverse
# Añadimos para poder usar reverse en get_absolute_url
from django.urls import reverse
from django.contrib.auth.models import User

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


# Review para Destination
class DestinationReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews'  # Obligatorio para tu código
    )
    rating = models.PositiveSmallIntegerField(default=10)  
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination')  # Cada usuario solo puede opinar una vez
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.destination.name} ({self.rating})"

# Review para Cruise
class CruiseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.CASCADE,
        related_name='reviews'  # Obligatorio
    )
    rating = models.PositiveSmallIntegerField(default=10)  # 1 a 10
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cruise')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.cruise.name} ({self.rating})"

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, null=True, blank=True, on_delete=models.CASCADE)
    cruise = models.ForeignKey(Cruise, null=True, blank=True, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.destination:
            return f"{self.user.username} purchased {self.destination.name}"
        else:
            return f"{self.user.username} purchased {self.cruise.name}"

