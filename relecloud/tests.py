from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Destination

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