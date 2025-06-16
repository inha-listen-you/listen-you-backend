import json
import uuid

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
        """c_로 시작하는 랜덤 해시값 대신 표준 UUID를 생성합니다."""
        
        # 표준 UUID (Version 4) 생성
        counsel_id_uuid = uuid.uuid4()
        
        current_time = datetime.now()
        
        return Response({
            'counsel_id': str(counsel_id_uuid),  # UUID 객체를 문자열로 변환하여 전달
            'created_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
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
                """UPDATE consult_log 
                   SET user_id = %s,
                       consel_history = %s,
                       report = %s
                   WHERE counsel_id = %s""",
                [user_id, counsel_history_str, report_str, counsel_id]
            )
        return Response(report)