from rest_framework import serializers
import uuid

# waitlist serializers
class WaitlistSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()

    class Meta:
        fields = ['name', 'email']


# user serializers


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True)
    date_joined = serializers.DateTimeField()
    last_login = serializers.DateTimeField()

    class Meta:
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    class Meta:
        fields = ['email', 'password']
