
from django.http import HttpResponse, JsonResponse
from django.views import View
from functions.db_actions import DBActions
from core.models import User, Waitlist
from core.serializers import UserLoginSerializer, UserSerializer, WaitlistSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
import jwt
from functions.supabase_client import supabase, secret


# JWT Token validation
class ValidateTokenView(APIView):
    permission_classes = []  # Publicly accessible

    def post(self, request, *args, **kwargs):
        # Extract token from the request
        token = request.data.get("token", None)
        if not token:
            raise AuthenticationFailed("Token is required.")

        try:
            # Decode the token
            decoded_token = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

        # If valid, return success
        return Response({"message": "Token is valid"})




class UserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        # Assume middleware has already validated the token and added the user info
        decoded_token = getattr(request, "decoded_token", None)

        if not decoded_token:
            # Middleware should have added this. If it's missing, raise an error.
            raise AuthenticationFailed("Decoded token missing. Ensure middleware is working correctly.")

        user_id = decoded_token.get("sub")  # 'sub' corresponds to the user ID in Supabase
        if not user_id:
            raise AuthenticationFailed("Token is missing user information.")

        # Fetch user details from the database
        response = DBActions().get('users', user_id)

        # Check if the user exists
        if not response.data or len(response.data) == 0:
            raise AuthenticationFailed("User not found in Supabase.")

        # Return the user data
        user = response.data
        return Response(user)
    
    
# Waitlist
class WaitlistView(APIView):
    permission_classes = [AllowAny] 
    serializers = WaitlistSerializer
    
    def post(self, request):
        serializer = self.serializers(data=request.data)
        if serializer.is_valid():
            try:
                waitlist = DBActions().create('waitlist', serializer.validated_data)
                return Response(waitlist, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Failed to create waitlist: {e}")
                return Response({"msg": "Failed to create waitlist", "error": e}, status=status.HTTP_400_BAD_REQUEST)
                
        print("Serializer failed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CreateUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        try: 
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                
                # Register user with Supabase Auth
                response = supabase.auth.sign_up({
                    'email': email,
                    'password': password,
                    'options': {
                        'data': {
                            'displayName': serializer.validated_data['first_name'] + serializer.validated_data['last_name']
                        }
                    }
                })

                
                if response and response.user:
                    user_id = response.user.id  # Get the user's ID from Supabase Auth
                    
                    # Prepare data for users table
                    data = serializer.validated_data
                    data.pop('password')  # Remove sensitive data
                    data['id'] = user_id  # Link user ID from Auth

                    # Insert into the users table
                    user = DBActions().create('users', data)
                    
                    login_response = supabase.auth.sign_in_with_password({
                        'email': email,
                        'password': password
                    })
                    
                    if login_response and login_response.session:
                        access_token = login_response.session.access_token
                        refresh_token = login_response.session.refresh_token
                        result = {
                            'user': user.data,
                            'access_token': access_token,
                            'refresh_token': refresh_token
                        }
                        return Response(result, status=status.HTTP_201_CREATED)
                    else:
                        return Response(
                            {"error": "Failed to login user in Supabase Auth"},
                            status=status.HTTP_400_BAD_REQUEST)
                
                else:
                    return Response(
                        {"error": "Failed to sign up user in Supabase Auth"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            print(f"Failed to create user: {e}")
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
            
            print("Login initiated: ", response)

            # Check if login was successful
            if response and response.session:
                user_id = response.user.id  # Supabase Auth User ID
                
                # Fetch user data from table
                user = DBActions().get('users', user_id)

                # Handle the response correctly
                if user.data:
                    # Extract tokens from the session object
                    access_token = response.session.access_token
                    refresh_token = response.session.refresh_token 

                    # Return the necessary data
                    result = {
                        'user': user.data,  # Data from your 'users' table
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                    }
                    return Response(result, status=status.HTTP_200_OK)
                # elif user.error:
                #     # Return a custom error message for missing user details
                #     return Response(
                #         {"error": "User details not found in database"},
                #         status=status.HTTP_404_NOT_FOUND
                #     )
            
            # Handle login failure
            return Response(
                {"error": "Failed to login user"},
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


# Refresh token endpoint

class RefreshTokenView(APIView):
    """
    A class-based view to handle refreshing tokens using Supabase.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("Received refresh call: ", request)
        
        try:
            # Extract the refresh_token from the JSON body
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return JsonResponse({"error": "Refresh token is required"}, status=400)

            # Call Supabase to refresh the session
            response = supabase.auth.refresh_session(refresh_token)
            
            # Return the new response.session details
            return JsonResponse({
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                # "expires_in": response.session.expires_in,
                # "user": session.user
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Return error if Supabase call fails or any unexpected error occurs
            return JsonResponse({"error": str(e)}, status=500)
