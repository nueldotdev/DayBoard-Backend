from rest_framework import serializers
from django.db import models
from django.utils.text import slugify
from functions.db_actions import DBActions
from .models import Board, List
import uuid


# board serializers

class BoardSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(required=True)
    creator_id = serializers.UUIDField(required=True)
    description = serializers.CharField(required=False, default='', allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    favorite = serializers.BooleanField(default=False)
    color = serializers.CharField(required=False, default='', allow_blank=True)
    image = serializers.CharField(required=False, default='', allow_blank=True)

    def save(self, **kwargs):
        db = DBActions()
        board_id = self.initial_data.get('id') 
        validated_data = self.validated_data
        validated_data['slug'] = slugify(validated_data['name'])
        validated_data['creator_id'] = str(validated_data['creator_id'])  # Ensure creator_id is JSON Serializable
        # add_to_board = db.get('boards', board_id)
        
        if board_id:
            return db.update('boards', validated_data, board_id)
        else:
            return db.create("boards", validated_data)

    class Meta:
        fields = ['id', 'slug', 'name', 'creator_id', 'description', 'created_at', 'favorite', 'color']
        read_only_fields = ['slug', 'created_at']



# List Serializers
class ListSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    board_id = serializers.UUIDField(required=True)
    title = serializers.CharField(required=True)
    position = serializers.IntegerField(required=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ['id', 'board_id', 'title', 'position', 'created_at']
        read_only_fields = ['created_at']