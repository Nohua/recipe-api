"""
    Test para el User API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
PAYLOAD = {
    'email': 'test@test.com',
    'password': 'testpass123',
    'name': 'Test Name',
}
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Crea y retorna el usuario creado"""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test para las opciones/caracteristicas de user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test para la creacion de usuario exitosa"""
        res = self.client.post(CREATE_USER_URL, PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=PAYLOAD['email'])
        self.assertTrue(user.check_password(PAYLOAD['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exist_error(self):
        """Test para retornar error si el usuario existe"""
        create_user(**PAYLOAD)
        res = self.client.post(CREATE_USER_URL, PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """
            Test para retornar un error si la contrasena
            es menor que 8 caracteres
        """
        PAYLOAD['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=PAYLOAD['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Generacion de token para validar las credenciales"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test que retorna que las credenciales son invalidas"""
        create_user(email='test@test.com', password='goodpass')
        payload = {'email': 'test@test.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test para retornar error si la contrasena esta en blanco"""
        payload = {'email': 'test@test.com', 'passowrd': ''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_anauthorized(self):
        """Test para requerir autenticacion para los users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API para solicitudes que requieres autenticacion"""

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass123',
            name='Test Name X'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test para recuperar el perfil para el user logeado"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST no esta permitido para el 'me' endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test Actualizar el perfil de user para un user autenticado"""
        payload = {'name': 'Update name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
