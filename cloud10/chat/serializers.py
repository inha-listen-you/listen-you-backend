from rest_framework import serializers
from .models import ConsultLog

class ConsultLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultLog
        fields = '__all__'