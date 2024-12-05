from rest_framework import serializers
from .models import User, Board

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'image', 'first_name', 'last_name', 'email', 'date_joined', 'last_login']


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['image', 'first_name', 'last_name', 'email', 'password']
