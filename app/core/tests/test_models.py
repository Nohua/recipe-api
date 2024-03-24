"""
Unit test para modelos
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    """Test Modelos"""

    def test_create_user_with_email_successful(self):
        """Test crear usuario con email"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email normalizado"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test crear usuario sin email y levante un ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test para crear un superusuario"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test para la creacion exitosa de una receta/recipe"""
        user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Ejemplo de nombre de receta',
            time_minutes=5,
            price=Decimal('6.99'),
            description='Ejemplo de descripcion de receta',
        )
        self.assertEqual(str(recipe), recipe.title)
