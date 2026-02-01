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
        db = DBActions(use_admin=True)
        board_id = self.initial_data.get('id') 
        validated_data = self.validated_data
        base_slug = slugify(validated_data['name'])
        validated_data['slug'] = self.get_unique_slug(db, base_slug, board_id)
        validated_data['creator_id'] = str(validated_data['creator_id'])  # Ensure creator_id is JSON Serializable
        # add_to_board = db.get('boards', board_id)
        
        if board_id:
            return db.update('boards', validated_data, board_id)
        else:
            return db.create("boards", validated_data)
    
    def get_unique_slug(self, db, base_slug, board_id=None):
        """
        Generate a unique slug by checking for conflicts in the database.
        If a conflict is found, appends a number to make it unique.
        
        Args:
            db: DBActions instance
            base_slug (str): The base slug to check
            board_id (str, optional): The current board ID (to exclude from uniqueness check during updates)
        
        Returns:
            str: A unique slug that doesn't exist in the database
        """
        slug = base_slug
        counter = 1
        
        while True:
            # Check if slug already exists
            response = db.get_by_field('boards', 'slug', slug)
            
            if response and response.data:
                # If updating and the existing slug is the current board's slug, it's OK
                if board_id and len(response.data) == 1 and response.data[0]['id'] == board_id:
                    return slug
                # Otherwise, generate a new slug with counter
                slug = f"{base_slug}-{counter}"
                counter += 1
            else:
                # Slug doesn't exist, we can use it
                return slug

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
    
    def save(self, **kwargs):
        db = DBActions(use_admin=True)
        list_id = self.initial_data.get('id') 
        validated_data = self.validated_data
        validated_data['board_id'] = str(validated_data['board_id'])  # Ensure board_id is JSON Serializable
        
        if list_id:
            # Handle position change repositioning
            old_list = db.get('lists', str(list_id))
            if old_list and old_list.data:
                old_position = old_list.data[0].get('position')
                new_position = validated_data.get('position')
                
                if old_position != new_position:
                    self._reposition_lists(db, validated_data['board_id'], old_position, new_position)
            
            return db.update('lists', validated_data, str(list_id))
        else:
            return db.create("lists", validated_data)
    
    def _reposition_lists(self, db, board_id, old_position, new_position):
        """
        Automatically reposition all lists when a list's position changes.
        
        Example: If list moves from position 4 to position 2:
        - Position 2 becomes 3
        - Position 3 becomes 4
        
        Args:
            db: DBActions instance
            board_id (str): The board ID
            old_position (int): The old position of the list
            new_position (int): The new position of the list
        """
        # Get all lists in this board
        response = db.get_many('lists', 'board_id', str(board_id))
        
        if not response or not response.data:
            return
        
        lists = response.data
        updates = []
        
        # If moving to a lower position (e.g., 4 to 2), shift others down
        if new_position < old_position:
            for list_item in lists:
                pos = list_item['position']
                if new_position <= pos < old_position:
                    updates.append({
                        'id': list_item['id'],
                        'position': pos + 1
                    })
        
        # If moving to a higher position (e.g., 2 to 4), shift others up
        elif new_position > old_position:
            for list_item in lists:
                pos = list_item['position']
                if old_position < pos <= new_position:
                    updates.append({
                        'id': list_item['id'],
                        'position': pos - 1
                    })
        
        # Batch update all affected lists in one call
        if updates:
            db.batch_update('lists', updates)

    class Meta:
        fields = ['id', 'board_id', 'title', 'position', 'created_at']
        read_only_fields = ['created_at']