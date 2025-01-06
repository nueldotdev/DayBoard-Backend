# Our endpoints

from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('current_user/', views.UserView.as_view(), name='current_user'),
  path('create_user/', views.CreateUserView.as_view(), name='create_user'),
  path('update_user/', views.UpdateUser.as_view(), name='update_user'),
  path('login_user/', views.LoginUser.as_view(), name='login_user'),
  
  
  path('add-to-waitlist/', views.WaitlistView.as_view(), name='add-to-waitlist'),
]