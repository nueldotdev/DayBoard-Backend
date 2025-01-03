# filepath: /c:/Users/walte/Documents/dev/DayBoard-Backend/core/views.py
from http.client import responses
from django.http import HttpResponse
from django.shortcuts import render
from core.functions.db_actions import DBActions
from core.models import User
from core.serializers import UserLoginSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from .supabase_client import supabase

def index(request):
  return HttpResponse("<h1>Hello, world. You're at the core index.</h1>")

@api_view(['GET'])
def current_user(request):
  serializer = UserSerializer(request.user)
  return Response(serializer.data)

class UserView(APIView):
  model = User
  serializer_class = UserSerializer

  def get(self, request, *args, **kwargs):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)




class CreateUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Register user with Supabase Auth
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            if response and response.user:
                user_id = response.user.id  # Get the user's ID from Supabase Auth
                
                # Prepare data for users table
                data = serializer.validated_data
                data.pop('password')  # Remove sensitive data
                data.pop('image')  # Remove sensitive data
                data['id'] = user_id  # Link user ID from Auth

                try:
                    # Insert into the users table
                    user = DBActions().create('users', data)
                    return Response(user, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(f"Failed to create user in Supabase: {e}")
                    return Response(
                        {"error": "Failed to create user in the database"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": "Failed to sign up user in Supabase Auth"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Log in the user with Supabase Auth
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            # Check if login was successful
            if response and response.session:
                user_id = response.user.id  # Supabase Auth User ID
                
                # Fetch additional user details from your custom "users" table
                user_data = supabase.table('users').select('*').eq('id', user_id).single().execute()

                # Handle the response correctly
                if user_data.data:
                    # Extract tokens from the session object
                    access_token = response.session.access_token
                    refresh_token = response.session.refresh_token

                    # Return the necessary data
                    result = {
                        'user': user_data.data,  # Data from your 'users' table
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                    }
                    return Response(result, status=status.HTTP_200_OK)
                elif user_data.error:
                    # Return a custom error message for missing user details
                    return Response(
                        {"error": "User details not found in custom 'users' table"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Handle login failure
            return Response(
                {"error": "Failed to login user in Supabase Auth"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle invalid serializer data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateUser(APIView):
  model = User
  serializer_class = UserSerializer

  def put(self, request, *args, **kwargs):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
      # Update user in Supabase
      data = serializer.validated_data
      response = supabase.table('users').update(data).eq('id', request.user.id).execute()
      if response.status_code == 200:
        return Response(serializer.data, status=200)
      return Response(response.json(), status=response.status_code)
    return Response(serializer.errors, status=400)