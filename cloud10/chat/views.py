from rest_framework.views import APIView
from rest_framework.response import Response
import uuid

class RandomHashView(APIView):
    def get(self, request):
        """c_로 시작하는 랜덤 해시값 생성"""
        random_hash = f"c_{uuid.uuid4().hex[:16]}"
        return Response({
            'hash': random_hash
        })
