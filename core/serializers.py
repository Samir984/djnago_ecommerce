from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer,
)
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        model = (
            BaseUserCreateSerializer.Meta.model
        )  # Ensure the model is correctly referenced
        fields = ["id", "username", "password", "email", "first_name", "last_name"]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):  # Properly extend the Meta class
        model = (
            BaseUserSerializer.Meta.model
        )  # Ensure the model is correctly referenced
        fields = ["id", "username", "first_name", "last_name"]
