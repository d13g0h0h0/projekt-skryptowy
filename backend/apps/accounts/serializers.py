from rest_framework import serializers

from .auth import scopes_for
from .models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class MeSerializer(serializers.ModelSerializer):
    scopes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "scopes"]

    def get_scopes(self, user) -> list[str]:
        return scopes_for(user)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)