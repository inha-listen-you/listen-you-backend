from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer


# 유저 정보 조회
class UserInfoView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            user_data = [{
                'id': user.id,
                'username': user.username,
                'pasword' : user.password,
                'consult_list' : user.consult_list
            } for user in users]
            return Response(user_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
