from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Destination
from django.urls import reverse

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

        # Comprobar que la respuesta es correcta y no contiene una URL de imagen
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'img src=')