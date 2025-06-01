from rest_framework import serializers

# 유저 정보 시리얼라이저
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField()
    