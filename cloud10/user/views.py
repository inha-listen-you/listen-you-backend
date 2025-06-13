from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from chat.models import ConsultLog
from django.shortcuts import get_object_or_404


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


class UserConsultDateView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    'message': '사용자 ID를 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 사용자 조회
            user = get_object_or_404(User, id=user_id)
            
            # 사용자의 consult_list가 없는 경우
            if not user.consult_list:
                return Response({
                    'message': '상담 내역이 없습니다.',
                    'consult_list': []
                }, status=status.HTTP_200_OK)
            
            # 각 counsel_id에 대한 상담 로그 조회
            consult_details = []
            for counsel_id in user.consult_list:
                try:
                    consult_log = ConsultLog.objects.get(counsel_id=counsel_id)
                    consult_details.append({
                        'counsel_id': str(counsel_id),
                        'created_at': consult_log.created_at
                    })
                except ConsultLog.DoesNotExist:
                    # 상담 로그가 없는 경우 해당 ID는 건너뜀
                    continue
            
            return Response({
                'message': '상담 내역 조회 성공',
                'user_id': user.id,
                'username': user.username,
                'consult_details': consult_details
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'message': '존재하지 않는 사용자입니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': f'상담 내역 조회 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)