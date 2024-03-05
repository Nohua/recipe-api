"""
    Serializers para la Vista de la APi de user
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el objecto user"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Crea y retorna un user con la contrasena encriptada"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update y retorna el user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer para el token de user auth"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validacion y autenticacion del user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            message = _(
                'Implosible autenticar con las credenciales ingresadas')
            raise serializers.ValidationError(message, code='authorization')
        attrs['user'] = user
        return attrs
