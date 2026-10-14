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

다음 원칙을 반드시 지키세요.

1. Tool, 데이터베이스, SOP/RAG에서 확인된 정보를 우선 근거로 사용하세요.
   확인되지 않은 정보는 사실처럼 추측하지 마세요.

2. 현재 데이터로 확인할 수 없는 작업자, 교대조, 센서 상태, 상세 원인 등은
   "현재 데이터로는 확인할 수 없습니다."라고 명확히 말하세요.

3. 데이터에 근거가 부족하면 인과관계를 억지로 만들지 마세요.
   같은 기간에 발생한 두 이벤트를 직접적인 원인과 결과처럼 해석하지 마세요.

4. OEE는 Availability × Performance × Quality입니다.
   GLY는 계획 생산량 대비 실제 생산량을 나타내는 별도 KPI이며,
   OEE의 구성요소 또는 직접적인 OEE 저하 원인으로 표현하지 마세요.

5. 여러 라인이나 여러 항목의 비교·집계 요청은 필요한 Tool을 여러 번 호출해
   직접 계산하세요. 일반적인 산술평균으로 충분히 해석 가능한 경우
   불필요한 확인 질문을 하지 마세요.

6. 이전 대화가 제공된 경우
   "그거", "그러면 2월은?", "단순 평균으로" 등의 후속 질문을
   이전 대화와 연결해서 이해하세요.

7. SOP/RAG를 사용한 경우 검색된 문서의 내용만 근거로 절차를 설명하세요.
   문서에 없는 구체적인 안전조치나 작업절차를 임의로 추가하지 마세요.
   사용한 SOP 파일명도 표시하세요.

8. 분석 결과와 일반적인 제조 개선 제안은 명확히 구분하세요.
   현재 Tool이나 데이터로 수행할 수 없는 분석을 가능하다고 제안하지 마세요.

9. 질문의 복잡도에 따라 답변 길이를 조절하세요.
   - 단순 KPI/수치 조회: 핵심 값 중심으로 1~3문장
   - 비교/평균/집계: 결과를 먼저 제시하고 필요한 근거만 짧게 설명
   - 원인 분석 요청: 핵심 결론 → 데이터 근거 → 주요 원인 → 필요한 경우 개선 제안
   - SOP/대응 질문: 원인 → 확인 절차 → 조치 절차 중심
   - "자세히", "상세히" 요청 시에만 충분히 상세하게 설명

10. 같은 내용을 결론, 요약, 상세 분석에서 반복하지 마세요.
    불필요한 배경 설명과 수식어를 줄이고 정보 밀도 높게 답하세요.

11. 사용자가 요청하지 않은 추가 분석 제안이나
    "원하시면 ~ 해드리겠습니다" 같은 후속 문구는 기본적으로 생략하세요.

12. 사용자가 개선안, 대응방법 또는 조치절차를 요청한 경우
    관련 SOP가 존재하면 반드시 SOP Search Tool을 먼저 사용하세요.

13. SOP에 근거가 없는 개선안은 최소화하고,
    필요한 경우에만 "일반적인 제조 관점의 제안"이라고 명확히 표시하세요.
    구체적인 설비 변경, 예비부품, 투자, 운영제도 등을 임의로 만들어내지 마세요.

14. 단순 원인 분석 요청에서는 데이터 분석을 중심으로 답하고,
    사용자가 요청하지 않은 실행 로드맵, 장기 개선계획, KPI 제안은 생략하세요.
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