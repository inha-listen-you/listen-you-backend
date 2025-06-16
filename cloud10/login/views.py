from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer
from user.models import User

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(username=username, password=password)
                return Response({
                    'message': '로그인 성공',
                    'user_id': user.id,
                    'username': user.username,
                    'consult_list': user.consult_list
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'message': '아이디 또는 비밀번호가 일치하지 않습니다.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원가입
class RegisterView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # username 중복 체크
            if User.objects.filter(username=username).exists():
                return Response({
                    'message': '이미 존재하는 사용자명입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 새 사용자 생성
            user = User.objects.create(
                username=username,
                password=password,
                consult_list=[]  # 빈 배열로 초기화
            )
            
            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)