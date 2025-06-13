from rest_framework import serializers
from .models import User
from django.utils import timezone

# 유저 정보 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','password','consult_list']
