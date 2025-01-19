# Our endpoints

from django.urls import path
from . import views

urlpatterns = [
  path('user/', views.UserView.as_view(), name='current_user'),
  path('update_user/', views.UpdateUser.as_view(), name='update_user'),
  
  path('auth/signup/', views.CreateUserView.as_view(), name='signup'),
  path('auth/login/', views.LoginUser.as_view(), name='login'),
  path('auth/refresh/', views.RefreshTokenView.as_view(), name='refresh-token'),
  path('auth/validate-token/', views.ValidateTokenView.as_view(), name='validate-token'),
  
  
  path('add-to-waitlist/', views.WaitlistView.as_view(), name='add-to-waitlist'),
]