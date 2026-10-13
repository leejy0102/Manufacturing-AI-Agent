# Manufacturing Agent의 LangGraph 기본 구조
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from app.tools.manufacturing_tools import (
    production_data_tool,
    kpi_summary_tool,
    downtime_summary_tool,
    performance_loss_summary_tool,
    quality_summary_tool,
    planned_downtime_summary_tool,
    sop_search_tool,
)

# .env 불러오기
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

# Tool 목록
tools = [
    production_data_tool,
    kpi_summary_tool,
    downtime_summary_tool,
    performance_loss_summary_tool,
    quality_summary_tool,
    planned_downtime_summary_tool,
    sop_search_tool,
]

# LLM 생성
llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# LLM에 Tool 연결
llm_with_tools = llm.bind_tools(tools)


# # Agent Node -> 이건 너무 과하게 답변해서 바로 아래에 시스템 프롬프트 추가
# # 현재까지의 메시지를 LLM에 전달하고,
# # Tool 호출이 필요한지 또는 최종 답변할지 판단
# def agent_node(state: MessagesState):
#     response = llm_with_tools.invoke(state["messages"])

#     return {
#         "messages": [response]
#     }


# Agent Node
# System Prompt를 함께 전달해서
# DB에 없는 내용을 추측하지 않고 제조 데이터 기반으로 답변하도록 제어

from langchain_core.messages import SystemMessage

SYSTEM_PROMPT = """
당신은 제조 현장의 생산 데이터를 분석하는 Manufacturing Intelligence Agent입니다.

반드시 다음 원칙을 지키세요.

1. Tool과 데이터베이스에서 확인된 데이터를 우선 근거로 사용하세요.
2. 데이터베이스에 존재하지 않는 정보는 사실처럼 추측하지 마세요.
3. 작업자, 교대조, 담당자, 설비 센서 상태 등 조회되지 않은 정보가 필요하면
   "현재 데이터로는 확인할 수 없습니다."라고 명확히 말하세요.
4. 숫자와 KPI를 제시할 때는 가능한 경우 실제 Tool 조회 결과를 근거로 사용하세요.
5. 분석 결과와 개선 제안을 구분하세요.
6. 개선 제안은 일반적인 제조 관점의 권고임을 명확히 표현하세요.
7. 사용자가 단순한 KPI 값을 물으면 불필요하게 긴 분석을 하지 마세요.
8. 원인 분석을 요청한 경우에는 다음 순서로 간결하게 답변하세요.
   - 핵심 결론
   - 데이터 근거
   - 주요 원인
   - 개선 제안
9. 데이터에 근거가 부족하면 억지로 결론을 만들지 마세요.
10. OEE는 Availability와 Performance, 그리고 Quality의 곱으로 계산됩니다.
    GLY는 계획 생산량 대비 실제 생산량을 나타내는 별도 KPI이며,
    GLY를 OEE의 구성요소 또는 OEE 저하의 직접 원인으로 표현하지 마세요.
11. 현재 데이터 또는 Tool로 수행할 수 없는 분석을
    "추가 분석 가능" 또는 선택지 형태로 제안하지 마세요.
12. SOP 또는 RAG 검색 결과에 명시되지 않은 구체적인 안전조치,
    설비조치, 작업절차를 사실처럼 추가하지 마세요.
13. SOP 검색 결과를 사용한 경우,
    답변에 참고한 SOP 파일명을 명확히 표시하세요.
14. 현재 DB 또는 SOP에 존재하지 않는 추가 분석이나 데이터 항목을
    수행 가능하다고 제안하지 마세요.
"""

def agent_node(state: MessagesState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# Tool 실행 Node
# LLM이 선택한 Tool을 실제로 실행
tool_node = ToolNode(tools)


# Agent가 Tool을 호출했는지 확인하는 조건 함수
def should_continue(state: MessagesState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# LangGraph 구성
builder = StateGraph(MessagesState)

# Node 등록
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# 시작점
builder.add_edge(START, "agent")

# Agent → Tool 또는 종료
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    }
)

# Tool 실행 후 다시 Agent로 돌아감
builder.add_edge("tools", "agent")

# 최종 Agent 컴파일
manufacturing_agent = builder.compile()