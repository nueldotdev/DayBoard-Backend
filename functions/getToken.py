from rest_framework.exceptions import AuthenticationFailed

def getTokenFromMiddleware(request):
  decoded_token = getattr(request, "decoded_token", None)

  if not decoded_token:
    raise AuthenticationFailed("Decoded token missing. Ensure middleware is working correctly.")

  user_id = decoded_token.get("sub")  # 'sub' corresponds to the user ID in Supabase
  if not user_id:
    raise AuthenticationFailed("Token is missing user information.")
  
  return user_id