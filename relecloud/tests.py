from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Cruise, Destination, InfoRequest, DestinationReview, CruiseReview, Purchase
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.core import mail
from django.conf import settings

# Create your tests here.
class DestinationModelTest(TestCase):
    def test_create_destination_with_image(self):
        # Crear una imagen simulada
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )
        
        # Crear una instancia de Destination con la imagen
        destination = Destination.objects.create(
            name='Test Destination',
            description='This is a test destination.',
            image=image
        )
        
        # Verificar que la instancia se creó correctamente
        self.assertEqual(destination.name, 'Test Destination')
        self.assertEqual(destination.description, 'This is a test destination.')
        self.assertIsNotNone(destination.image)
        self.assertTrue(destination.image.name.startswith('destinations/test_image'))


# Tests para la lista de destinos (rojo)
class DestinationListViewTest(TestCase):
    def test_destination_list_shows_image_if_present(self):
        # Crear una instancia de Destination con imagen
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )
        destination_with_image = Destination.objects.create(
            name='Destination With Image',
            description='This destination has an image.',
            image=image
        )
        
        url = reverse('destinations')
        response = self.client.get(url)

        # Comprobar que la imagen se muestra en la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, destination_with_image.image.url)


    def test_destination_list_renders_without_image(self):
        # Crear una instancia de Destination sin imagen
        destination_without_image = Destination.objects.create(
            name='Destination Without Image',
            description='This destination does not have an image.'
        )
        
        url = reverse('destinations')
        response = self.client.get(url)

        # Comprobar que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        # Comprobar que aparece el destino en la lista
        self.assertContains(response, destination_without_image.name)

# Tests para el detalle de destino 
class DestinationDetailViewTests(TestCase):
    def test_destination_detail_shows_image_if_present(self):
        image = SimpleUploadedFile(
            "detail_test_image.jpg",
            b"filecontent",
            content_type="image/jpeg"
        )

        destination = Destination.objects.create(
            name="Detalle con imagen",
            description="Descripción del destino con imagen",
            image=image
        )

        url = reverse('destination_detail', kwargs={'pk': destination.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, destination.image.url)

    def test_destination_detail_renders_without_image(self):
        destination = Destination.objects.create(
            name="Detalle sin imagen",
            description="Descripción sin imagen"
        )

        url = reverse('destination_detail', kwargs={'pk': destination.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detalle sin imagen")

# Tests para envío de solicitudes de información (InfoRequest)
class InfoRequestEmailTests(TestCase):
    def setUp(self):
        self.cruise = Cruise.objects.create(
            name='Caribbean Cruise',
            description='Un encantador crucero por el Caribe.'
        )

    def test_info_request_email_sent(self):
        # Crear una solicitud de información
        response = self.client.post(reverse('info_request'), {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'notes': 'Quería más información del crucero.',
            # Usamsos el ID del crucero creado en setUp
            'cruise': self.cruise.pk
        })

        # Comprobar que se ha enviado un email (debe existir un email en la bandeja de salida)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Información sobre Caribbean Cruise', email.subject)
        self.assertIn('Hola Test User', email.body)
        self.assertIn('Gracias por tu interés en Caribbean Cruise', email.body)
        self.assertIn('Tendremos en cuenta tus notas: ', email.body)
        self.assertIn('Quería más información del crucero.', email.body)

        # Comprobar el destinatario del email
        self.assertEqual(email.to, ['testuser@example.com'])

    def test_info_request_email_redirection(self):
        # Crear una solicitud de información
        response = self.client.post(reverse('info_request'), {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'notes': 'Quería más información del crucero.',
            'cruise': self.cruise.pk
        })

        # Comprobar que la respuesta es una redirección
        self.assertEqual(response.status_code, 302)
        email_from = settings.EMAIL_HOST_USER
        self.assertEqual(mail.outbox[0].from_email, email_from)
        self.assertEqual(response.url, reverse('index'))


# P13 - Test para destinos reviews
class DestinationReviewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.destination = Destination.objects.create(
            name='Mars',
            description='Red planet adventure'
        )
        self.cruise = Cruise.objects.create(
            name='Mars Cruise',
            description='Travel to Mars!'
        )
        
    def test_add_destination_review_without_purchase(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('destination_review', args=[self.destination.pk]),
            {'rating': 8, 'comment': 'Great!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DestinationReview.objects.filter(user=self.user, destination=self.destination).exists())

    def test_add_destination_review_with_purchase(self):
        self.client.login(username='testuser', password='12345')
        Purchase.objects.create(user=self.user, destination=self.destination)
        response = self.client.post(
            reverse('destination_review', args=[self.destination.pk]),
            {'rating': 9, 'comment': 'Amazing experience!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DestinationReview.objects.filter(user=self.user, destination=self.destination).exists())

# P13 - Test para cruceros reviews
class CruiseReviewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.destination = Destination.objects.create(
            name='Venus',
            description='Hot planet adventure'
        )
        self.cruise = Cruise.objects.create(
            name='Venus Cruise',
            description='Travel to Venus!'
        )
        
    def test_add_cruise_review_without_purchase(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('cruise_review', args=[self.cruise.pk]),
            {'rating': 7, 'comment': 'Good trip!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CruiseReview.objects.filter(user=self.user, cruise=self.cruise).exists())

    def test_add_cruise_review_with_purchase(self):
        self.client.login(username='testuser', password='12345')
        Purchase.objects.create(user=self.user, cruise=self.cruise)
        response = self.client.post(
            reverse('cruise_review', args=[self.cruise.pk]),
            {'rating': 10, 'comment': 'Fantastic voyage!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CruiseReview.objects.filter(user=self.user, cruise=self.cruise).exists())


# P13 - Test para compras
class PurchaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.destination = Destination.objects.create(
            name='Jupiter',
            description='Giant planet adventure'
        )
        self.cruise = Cruise.objects.create(
            name='Jupiter Cruise',
            description='Travel to Jupiter!'
        )
        
    def test_buy_destination(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('buy_destination', args=[self.destination.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Purchase.objects.filter(user=self.user, destination=self.destination).exists())

    def test_buy_cruise(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('buy_cruise', args=[self.cruise.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Purchase.objects.filter(user=self.user, cruise=self.cruise).exists())

# P13 - Test para cálculo de valoraciones medias
class AverageRatingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='54321')
        self.cruise = Cruise.objects.create(
            name='Saturn Cruise',
            description='Travel to Saturn!'
        )   
    def test_average_rating_calculation(self):
        CruiseReview.objects.create(user=self.user1, cruise=self.cruise, rating=9, comment='Excellent!')
        CruiseReview.objects.create(user=self.user2, cruise=self.cruise, rating=7, comment='Very good!')

        avg_rating = CruiseReview.objects.filter(cruise=self.cruise).aggregate(models.Avg('rating'))['rating__avg']
        self.assertEqual(avg_rating, 8.0)

# Test para ordenar destinos por número de reviews
class DestinationOrderByReviewsTests(TestCase):
    def setUp(self):
        # Crear usuarios
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        
        # Crear destinos
        self.dest_mars = Destination.objects.create(name='Mars', description='Red planet')
        self.dest_venus = Destination.objects.create(name='Venus', description='Hot planet')
        self.dest_jupiter = Destination.objects.create(name='Jupiter', description='Giant planet')
        
        # Crear compras y reviews
        # Mars: 2 reviews
        Purchase.objects.create(user=self.user1, destination=self.dest_mars)
        Purchase.objects.create(user=self.user2, destination=self.dest_mars)
        DestinationReview.objects.create(user=self.user1, destination=self.dest_mars, rating=9, comment='Great!')
        DestinationReview.objects.create(user=self.user2, destination=self.dest_mars, rating=8, comment='Good!')
        
        # Venus: 1 review
        Purchase.objects.create(user=self.user1, destination=self.dest_venus)
        DestinationReview.objects.create(user=self.user1, destination=self.dest_venus, rating=7, comment='Nice!')
        
        # Jupiter: 0 reviews (solo creado, sin compras ni reviews)
    
    def test_destinations_ordered_by_review_count(self):
        """Test que los destinos se ordenan por número de reviews (descendente)"""
        url = reverse('destinations')
        response = self.client.get(url)
        destinations = response.context['destinations']
        
        # Verificar orden: Mars (2), Venus (1), Jupiter (0)
        self.assertEqual(destinations[0].name, 'Mars')
        self.assertEqual(destinations[0].review_count, 2)
        self.assertEqual(destinations[1].name, 'Venus')
        self.assertEqual(destinations[1].review_count, 1)
        self.assertEqual(destinations[2].name, 'Jupiter')
        self.assertEqual(destinations[2].review_count, 0)

