from rest_framework import serializers
from .models import User
from django.utils import timezone

# 유저 정보 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            created_at=timezone.now()
        )
        return user
    