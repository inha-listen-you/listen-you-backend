
import os
import json
from dotenv import load_dotenv
import boto3
from typing import TypedDict, List, Dict, Any

from langchain_aws import ChatBedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph, END

# 환경 변수 로드
load_dotenv()

# 상담 요약을 위한 프롬프트 템플릿
RAG_PROMPT_TEMPLATE = """
당신은 상담 내역을 분석하고 요약하는 전문가입니다.
아래 JSON 형식으로 제공된 상담 대화를 분석하여 다음 정보를 포함한 요약을 작성해 주세요:

1. 주요 문제: 사용자가 겪고 있는 핵심 문제점이나 고민
2. 감정 상태: 사용자의 전반적인 감정 상태나 태도
3. 주요 주제: 대화에서 다룬 중요한 주제들
4. 권장 사항: 상담 내용을 바탕으로 한 권장 사항이나 해결책

JSON 상담 내역:
{consultation_history}

요약 형식:
- 주요 문제: [사용자의 핵심 문제 요약]
- 감정 상태: [사용자의 감정 상태 분석]
- 주요 주제: [대화에서 다룬 중요 주제들]
- 권장 사항: [권장 사항 및 해결책]
"""

rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

# 상태 정의
class SummaryState(TypedDict):
    consult_history: str
    summary: str


# LLM 모델 설정

def get_llm():
    # model_id_from_user = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    llm = ChatBedrock(
        region_name="us-east-1",
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={
            # "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )
    return llm

# 요약 노드 정의
def summarize(state: SummaryState) -> SummaryState:
    consultation_history = state["consult_history"]

    chain = rag_prompt | get_llm() | StrOutputParser()

    response = chain.invoke({"consult_history": consultation_history})

    return {"consult_history": consultation_history, "summary": response}


# 그래프 구성
def get_graph():
    graph_builder = StateGraph(SummaryState)

    graph_builder.add_node("summarize", summarize)

    graph_builder.add_edge(START, "summarize")
    graph_builder.add_edge("summarize", END)

    return graph_builder.compile()