from rest_framework import serializers
from django.db import models
from .models import User, Board, List, Waitlist
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



# board serializers

class BoardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True) 
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default='')

    class Meta:
        model = Board
        fields = ['id', 'slug', 'name', 'creator', 'description', 'created_at']

    def create(self, validated_data):
        return Board.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


# List Serializers
class ListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True) 

    class Meta:
        model = List
        fields = ['id', 'board', 'title', 'position', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        board = validated_data['board']
        max_position = List.objects.filter(board=board).aggregate(models.Max('position'))['position__max']
        validated_data['position'] = (max_position or 0) + 1
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_position = instance.position
        new_position = validated_data.get('position', old_position)
        if old_position != new_position:
            instance.position = new_position
            instance.save()
        return instance