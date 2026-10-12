# LLM이 사용자 질문을 보고 적절한 제조 Tool을 선택하는지 테스트
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.tools.manufacturing_tools import (
    production_data_tool,
    kpi_summary_tool,
    downtime_summary_tool,
    performance_loss_summary_tool,
    quality_summary_tool,
    planned_downtime_summary_tool,
)

# 프로젝트 루트의 .env 불러오기
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# 사용할 Tool 목록
tools = [
    production_data_tool,
    kpi_summary_tool,
    downtime_summary_tool,
    performance_loss_summary_tool,
    quality_summary_tool,
    planned_downtime_summary_tool,
]

# LLM 생성
llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# LLM에 Tool 연결
llm_with_tools = llm.bind_tools(tools)

# 테스트 질문
question = "CAN1 라인의 2026년 1월 평균 OEE를 알려줘."

response = llm_with_tools.invoke(question)

print("LLM 응답:")
print(response)

print("\n선택된 Tool:")
print(response.tool_calls)