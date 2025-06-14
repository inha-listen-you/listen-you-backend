import json

from django.db import connection
from langchain_core.messages import HumanMessage
from langgraph_checkpoint_dynamodb.errors import DynamoDBCheckpointError
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from datetime import datetime
from .models import ConsultLog
from .serializers import ConsultLogSerializer


from langgraph.agent import get_graph, insert_counsel_data
from langgraph.summary_agent import get_graph as get_summary_graph




class RandomHashView(APIView):
    def get(self, request):
        """c_로 시작하는 랜덤 해시값 생성"""
        current_time = datetime.now()
        # 현재 시간을 마이크로초까지 포함한 타임스탬프로 변환
        timestamp = int(current_time.timestamp() * 100000)  # 마이크로초 단위로 변환

        # 타임스탬프를 16진수로 변환하고 8자리만 사용
        time_hash = hex(timestamp)[2:10]
        
        random_hash = f"c_{time_hash}"
        
        return Response({
            'counsel_id': random_hash,
            'created_at': current_time.strftime('%Y-%m-%d %H:%M:%S')  # 초 단위까지만 표시
        })

class GenerateAIMessageView(APIView):
    def post(self, request):
        print(f"[시작] GenerateAIMessageView.post 요청 시작: {datetime.now()}")

        counsel_id = request.data['counsel_id']
        query = request.data['query']
        user_id = request.data['user_id']

        graph = get_graph()

        state = {
            'messages': [HumanMessage(query)],
            'query': query,
            'context': []
        }

        config = {"configurable": {"thread_id": counsel_id}}

        try:
            response = graph.invoke(state, config=config)

            insert_counsel_data(user_id, counsel_id, response["messages"][-1].content, query)
            print(f"[종료] GenerateAIMessageView.post 요청 정상 완료: {datetime.now()}")

            return Response({
                'message': response['messages'][-1].content
            })

        except DynamoDBCheckpointError as exc:
            print(f"DynamoDBCheckpointError 발생: {exc}")
            if exc.__cause__:
                original_error = exc.__cause__
                print(f"원인 예외 타입: {type(original_error)}")
                print(f"원인 예외 메시지: {original_error}")
                if hasattr(original_error, 'response'):
                    print(f"원인 예외 응답: {original_error.response}")
            raise

        except Exception as exc:
            print(f"처리되지 않은 예외 발생: {exc}")
            import traceback

            print(traceback.format_exc())
            raise

class SummarizeConsultLogView(APIView):
    def post(self, request):
        user_id = request.data['user_id']
        counsel_id = request.data['counsel_id']
        counsel_history = request.data['counsel_history']
        state = {
            'consult_history': counsel_history
        }
        response = get_summary_graph().invoke(state)
        report = {
            'summary': response['summary'],
            'status': "completed"
        }

        counsel_history_str = json.dumps(counsel_history, ensure_ascii=False)
        report_str = json.dumps(report, ensure_ascii=False)

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO consult_log (user_id, counsel_id, consel_history, report) 
                   VALUES (%s, %s, %s, %s)""",
                [user_id, counsel_id, counsel_history_str, report_str]
            )
        return Response(report)