from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.utils.deprecation import MiddlewareMixin
from functions.supabase_client import secret  # Supabase secret key

class TokenValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip validation for open routes
        open_routes = ["/auth/validate-token/", "/auth/login/", "/auth/signup/", "/auth/refresh/", "/add-to-waitlist/", "/auth/google/", "/auth/google/callback/", "/auth/google/callback"]
        print("Route: ", request.path)
        
        if request.path in open_routes:
          return None

        # Check for Authorization header
        auth_header = get_authorization_header(request).decode("utf-8")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header is missing or invalid.")

        token = auth_header.split(" ")[1]  # Extract the token

        try:
            # Decode the token
            decoded_token = jwt.decode(
              token, 
              secret, 
              algorithms=["HS256"], 
              options={"verify_aud": False}
            )
            
            
            request.decoded_token = decoded_token
        
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

        # If valid, continue the request
