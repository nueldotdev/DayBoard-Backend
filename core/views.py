from django.http import HttpResponse
from django.shortcuts import render

from core.models import User
from core.serializers import CreateUserSerializer, UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

# Create your views here.


def index(request):
  admin = User.objects.get_or_create(email='admin@dayboard.com', username='admin', is_admin=True, first_name='Admin', last_name='Admin')

  print("This is admin: ", admin)

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
  
  


class CreateUser(APIView):
  model = User
  serializer_class = CreateUserSerializer

  def post(self, request, *args, **kwargs):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
  


class UpdateUser(APIView):
  model = User
  serializer_class = UserSerializer

  def put(self, request, *args, **kwargs):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
  