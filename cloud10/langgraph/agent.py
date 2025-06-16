import os
import datetime

import boto3

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from langchain_aws import ChatBedrock
from typing import TypedDict, Annotated, List, Union

from langgraph.graph.message import add_messages
from langgraph.graph.message import AnyMessage
from langgraph.graph import StateGraph
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import START, END

from langgraph_checkpoint_dynamodb import DynamoDBTableConfig, DynamoDBConfig, DynamoDBSaver

load_dotenv()

RAG_PROMPT_TEMPLATE = """
당신은 사용자의 질문에 친절하고 상세하게 답변하는 AI 상담가입니다.
주어진 이전 대화 내용과 참고 정보를 바탕으로 사용자의 현재 질문에 답변해주세요.
사용자에게 정신상담과 관련된 질문까지 생성해주면 좋습니다.
답변은 200자 이내로 작성해주세요.

[이전 대화 내용]
{messages}

[참고 정보]
{context}

[사용자 현재 질문]
{query}

[AI 답변]
"""

rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    query: str
    context: list
    # answer: str


# dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# TABLE_NAME = 'listen-you-full'
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

# CHECKPOINT_TABLE_NAME = 'listen-you-checkpoints'
CHECKPOINT_TABLE_NAME = os.environ['DYNAMODB_CHECKPOINT_TABLE_NAME']

checkpoint_table_config = DynamoDBTableConfig(table_name=CHECKPOINT_TABLE_NAME)
# checkpointer_config = DynamoDBConfig(table_config=checkpoint_table_config, endpoint_url='http://localhost:8000')
checkpointer_config = DynamoDBConfig(table_config=checkpoint_table_config, region_name='us-east-1')
checkpointer = DynamoDBSaver(config=checkpointer_config, deploy=False)


def get_llm_local():
    llm = OpenAI(model="gpt-4o-mini")
    return llm

def get_llm():
    # model_id_from_user = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    llm = ChatBedrock(
        region_name="us-east-1",
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={
            # "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
    return llm

def generate(state: AgentState):
    query = state['query']
    messages = state['messages']
    context = state['context']

    chain = (rag_prompt
        | get_llm()
        | StrOutputParser())

    response = chain.invoke({'query': query, 'messages': messages, 'context': context, })

    return {'messages': [AIMessage(content=response)]}

def get_graph():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node('generate', generate)

    graph_builder.add_edge(START, 'generate')
    graph_builder.add_edge('generate', END)
    return graph_builder.compile(checkpointer=checkpointer)

def insert_counsel_data(user_id, counsel_id, ai_answer, user_input):
    try:
        current_timestamp = str(datetime.datetime.now(datetime.timezone.utc).isoformat())

        response = table.put_item(
            Item={
                'user_id': str(user_id),
                'timestamp': current_timestamp,
                'counsel_id': counsel_id,
                'ai_answer': ai_answer,
                'user_input': user_input,
            }
        )
        print(f"Inserted {user_input} into {counsel_id}")
        return response
    except ClientError as e:
        print(f"데이터 삽입 중 오류 발생 : {e.response['Error']['Message']}")
        return None

def get_user_counsel_data(user_id):
    response = table.query(KeyConditionExpression=Key('user_id').eq(user_id))

    if response['Items']:
        for item in response['Items']:
            print(f"user_id: {item['user_id']}, timestamp: {item['timestamp']}, ai_answer: {item['ai_answer']}")


def get_counsel_data(counsel_id):
    response = table.query(IndexName='counsel_id-timestamp-index', KeyConditionExpression=Key('counsel_id').eq(counsel_id))

    if response['Items']:
        for item in response['Items']:
            print(f"user_id: {item['user_id']}, timestamp: {item['timestamp']}, ai_answer: {item['ai_answer']}")