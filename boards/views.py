from django.http import HttpResponse, JsonResponse
from django.views import View
from functions.db_actions import DBActions
from boards.serializers import BoardSerializer, ListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
import jwt
from functions.getToken import getTokenFromMiddleware
from functions.supabase_client import supabase, secret
import logging


class CreateBoardView(APIView):
  permission_classes = [AllowAny]
  serializer_class = BoardSerializer
  
  def post(self, request):
    try:
      user_id = getTokenFromMiddleware(request)
      
      if not user_id:
        raise AuthenticationFailed("Token is missing user information.")
    
      name = request.data.get('name')
      creator_id = user_id
      
      data = {
        'name': name,
        'creator_id': creator_id
      }
      
      serializer = BoardSerializer(data=data)
      if serializer.is_valid():
        board = serializer.save()
        return Response({'message': 'Board created successfully', 'board': board.data}, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      logger = logging.getLogger(__name__)
      logger.error(f"Failed to create board: {e}")

      return Response({"msg": "Failed to create board"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class GetBoardsView(APIView):
  permission_classes = [AllowAny]
  
  def get(self, request):
    
    try:
      user_id = getTokenFromMiddleware(request)
      
      if not user_id:
        raise AuthenticationFailed("Token is missing user information.")
      
      boards = DBActions().get_many('boards', 'creator_id', user_id)
      
      if not boards.data or len(boards.data) == 0:
        return Response({"msg": "No boards found"}, status=status.HTTP_400_BAD_REQUEST)
      
      for board in boards.data:
        board.pop('creator_id')
      
      return Response(boards.data, status=status.HTTP_200_OK)
    except Exception as e:
      logger = logging.getLogger(__name__)
      logger.error(f"Failed to get boards: {e}")
      return Response({"msg": "Failed to get boards"}, status=status.HTTP_400_BAD_REQUEST)


class GetBoardInfoView(APIView):
  permission_classes = [AllowAny]
  
  def get(self, request, board_slug: str):
    db = DBActions()
    
    try:
      user_id = getTokenFromMiddleware(request)
          
      if not user_id:
        raise AuthenticationFailed("Token is missing user information.")
          
      board = db.get_many('boards', 'creator_id', user_id)
      
      if not board.data or len(board.data) == 0:
        return Response({"msg": "No board found"}, status=status.HTTP_400_BAD_REQUEST)
      
      for i in board.data:
        if i['slug'] == board_slug:
          return Response(i, status=status.HTTP_200_OK)
      
      return Response({"msg": "No board found"}, status=status.HTTP_400_BAD_REQUEST)
      
    except Exception as e:
      logger = logging.getLogger(__name__)
      logger.error(f"Failed to get board: {e}")
      return Response({"msg": "Failed to get board"}, status=status.HTTP_400_BAD_REQUEST)
    
    
  
class UpdateBoardView(APIView):
  permission_classes = [AllowAny]
  
  def put(self, request):
    # try:
      user_id = getTokenFromMiddleware(request)
          
      if not user_id:
        raise AuthenticationFailed("Token is missing user information.")
          
      updated_board = request.data.get('updatedBoard')
      board_id = request.data.get('boardId')
      
      board = DBActions().get('boards', board_id)
          
      if not board.data:
        return Response({"msg": "Board not found"}, status=status.HTTP_400_BAD_REQUEST)
          
      for i in board.data:
        if i['creator_id'] != user_id:
          return Response({"msg": "You are not authorized to update this board"}, status=status.HTTP_401_UNAUTHORIZED)
      
      
      data = {
        **board.data[0],
        **updated_board
      }

      serializer = BoardSerializer(board.data[0], data=data)
      if serializer.is_valid():
        board = serializer.save()
        return Response({'message': 'Board updated successfully', 'board': board.data}, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #   logger = logging.getLogger(__name__)
    #   logger.error(f"Failed to update board: {e}")
    #   return Response({"msg": "Failed to update board"}, status=status.HTTP_400_BAD_REQUEST)