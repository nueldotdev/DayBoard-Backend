from rest_framework import serializers
from django.db import models
from .models import User, Waitlist
import uuid

# waitlist serializers
class WaitlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Waitlist
        fields = ['name', 'email']


# user serializers


class UserSerializer(serializers.ModelSerializer):
    # Define a password field that is write-only and required
    password = serializers.CharField(write_only=True, required=True)
    id = serializers.UUIDField(read_only=True) 

    class Meta:
        # Specify the model to be serialized
        model = User
        # Define the fields to be included in the serialization
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'date_joined', 'last_login']
        # Ensure the password field is write-only
        extra_kwargs = {'password': {'write_only': True}}



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    class Meta:
        fields = ['email', 'password']
