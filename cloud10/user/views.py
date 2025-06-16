from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from chat.models import ConsultLog
from django.shortcuts import get_object_or_404
import json
from django.db import connection

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
                return Response({'message': '사용자 ID를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_404(User, id=user_id)
            counsel_id_list = user.consult_list

            if not counsel_id_list:
                return Response({'message': '상담 내역이 없습니다.', 'consult_list': []}, status=status.HTTP_200_OK)

            # --- Django ORM을 우회하는 Raw SQL 실행 ---
            # 1. 실행할 SQL 쿼리를 정의합니다. SQL 인젝션을 방지하기 위해 파라미터를 사용합니다.
            sql = "SELECT counsel_id, created_at, report FROM consult_log WHERE counsel_id IN %s"
            
            # 2. IN 절에 들어갈 파라미터는 반드시 튜플 형태여야 합니다.
            params = (tuple(counsel_id_list),)

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                # 컬럼 이름을 가져옵니다.
                columns = [col[0] for col in cursor.description]
                # 모든 데이터를 가져옵니다.
                rows = cursor.fetchall()

            # --- Raw SQL 결과 처리 ---
            # 3. 조회된 결과를 다루기 쉽게 딕셔너리(맵) 형태로 가공합니다.
            logs_map = {}
            for row in rows:
                log_data = dict(zip(columns, row))
                
                # `report` 필드가 문자열일 경우, 직접 파싱하여 dict으로 변환합니다.
                report = log_data.get('report')
                if isinstance(report, str):
                    try:
                        log_data['report'] = json.loads(report)
                    except json.JSONDecodeError:
                        log_data['report'] = None  # 파싱 실패 시 None으로 처리
                
                # UUID 객체를 키로 사용하여 맵에 저장합니다.
                logs_map[log_data['counsel_id']] = log_data
            
            # --- 최종 응답 데이터 구성 ---
            consult_details = []
            for counsel_id in counsel_id_list:
                log_data = logs_map.get(counsel_id)
                if log_data:
                    detail = {
                        'counsel_id': str(log_data['counsel_id']),
                        'created_at': log_data['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                        'report': log_data['report'] # 이제 report는 항상 dict 또는 None 입니다.
                    }
                    consult_details.append(detail)
            
            response_data = {
                'message': '상담 내역 조회 성공',
                'user_id': str(user.id),
                'consult_details': consult_details
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': '존재하지 않는 사용자입니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 예상치 못한 오류에 대한 상세 로그를 남깁니다.
            print(f"상담 내역 조회 중 심각한 오류 발생: {type(e).__name__} - {str(e)}")
            return Response({'message': f'상담 내역 조회 중 오류가 발생했습니다: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserLatestReportView(APIView):
    """
    (Raw SQL) 사용자의 가장 최근 상담 내역(counsel_id, report)을 조회합니다.
    """
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({'message': '사용자 ID를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_404(User, id=user_id)
            counsel_id_list = user.consult_list

            if not counsel_id_list:
                return Response({'message': '상담 내역이 없습니다.'}, status=status.HTTP_200_OK)

            # Raw SQL을 사용하여 가장 최신의 상담 내역 1개만 조회
            sql = """
                SELECT counsel_id, report, created_at
                FROM consult_log
                WHERE counsel_id IN %s
                ORDER BY created_at DESC
                LIMIT 1
            """
            params = (tuple(counsel_id_list),)

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone() 

            if not row:
                return Response({'message': '상담 기록을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            columns = [col[0] for col in cursor.description]
            latest_log_data = dict(zip(columns, row))

            report = latest_log_data.get('report')
            if isinstance(report, str):
                try:
                    latest_log_data['report'] = json.loads(report)
                except json.JSONDecodeError:
                    latest_log_data['report'] = None

            response_data = {
                'message': '최신 상담 내역 조회 성공',
                'user_id': str(user.id),
                'latest_consult': {
                    'counsel_id': str(latest_log_data['counsel_id']),
                    'report': latest_log_data['report']
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': '존재하지 않는 사용자입니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"최신 상담 조회 중 오류 발생: {type(e).__name__} - {str(e)}")
            return Response({'message': f'최신 상담 내역 조회 중 오류가 발생했습니다: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultReportView(APIView):
    """
    특정 counsel_id에 대한 상담 리포트를 조회합니다.
    """
    def post(self, request):
        try:
            counsel_id = request.data.get('counsel_id')
            if not counsel_id:
                return Response({
                    'message': '상담 ID를 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Raw SQL을 사용하여 특정 상담의 리포트 조회
            sql = """
                SELECT counsel_id, report, created_at
                FROM consult_log
                WHERE counsel_id = %s
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [counsel_id])
                row = cursor.fetchone()

            if not row:
                return Response({
                    'message': '해당 상담 기록을 찾을 수 없습니다.'
                }, status=status.HTTP_404_NOT_FOUND)

            columns = [col[0] for col in cursor.description]
            log_data = dict(zip(columns, row))

            # report가 문자열인 경우 JSON으로 파싱
            report = log_data.get('report')
            if isinstance(report, str):
                try:
                    log_data['report'] = json.loads(report)
                except json.JSONDecodeError:
                    log_data['report'] = None

            response_data = {
                'message': '상담 리포트 조회 성공',
                'counsel_id': str(log_data['counsel_id']),
                'created_at': log_data['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'report': log_data['report']
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"상담 리포트 조회 중 오류 발생: {type(e).__name__} - {str(e)}")
            return Response({
                'message': f'상담 리포트 조회 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)