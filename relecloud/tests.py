from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Cruise, Destination
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