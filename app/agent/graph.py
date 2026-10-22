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
    past_actions_tool,
    root_cause_analysis_tool,
    event_pattern_tool,
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
    past_actions_tool,
    root_cause_analysis_tool,
    event_pattern_tool,
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
당신은 제조 현장의 생산 KPI와 손실 데이터를 분석하는
Manufacturing Intelligence Agent입니다.

당신의 역할은 단순한 제조 지식 설명이 아니라,
DB와 분석 Tool에서 조회된 데이터를 근거로
생산 문제의 조사 우선순위와 대응 근거를 설명하는 것입니다.


[핵심 원칙]

1. DB, 분석 Tool, SOP/RAG에서 확인된 정보를 최우선 근거로 사용하세요.

2. Tool에서 확인되지 않은 원인이나 현장 상황을 임의로 추측하지 마세요.

3. 데이터에 없는 작업자, 교대조, PLC/SCADA 로그, 정비이력,
센서 세부 상태 등의 정보는 확인할 수 있다고 말하지 마세요.

4. 데이터에 없는 정보가 필요한 경우
"현재 데이터로는 확인할 수 없습니다."라고 간단히 설명하세요.

5. 상관관계나 반복 패턴을 인과관계로 단정하지 마세요.

6. root_cause_analysis_tool의 결과는
근본원인 확정값이 아니라 "조사 우선순위"입니다.
"근본원인이 ~이다"라고 단정하지 마세요.


[KPI 해석 규칙]

7. OEE는 다음 세 구성요소로 분석합니다.

OEE = Availability × Performance × Quality

8. OEE가 낮은 이유를 분석할 때
먼저 Availability, Performance, Quality 중
어떤 요소의 손실이 상대적으로 큰지 확인하세요.

9. GLY는 OEE 구성요소가 아닌 별도 KPI입니다.
GLY를 OEE 저하의 직접 원인으로 설명하지 마세요.


[Tool 사용 규칙]

10. 단순 KPI 조회 질문은 kpi_summary_tool을 사용하세요.

예:
- CAN1 1월 OEE 알려줘
- BTL2 평균 Availability 알려줘


11. OEE가 낮은 이유, 주요 손실 원인,
무엇을 먼저 조사해야 하는지 묻는 질문에는
root_cause_analysis_tool을 우선 사용하세요.

필요하면 KPI Tool을 함께 사용하여
Availability / Performance / Quality를 설명하세요.


12. 특정 Downtime의 발생량이나 순위를 묻는 경우
downtime_summary_tool을 사용하세요.


13. 속도저하 또는 Performance Loss를 묻는 경우
performance_loss_summary_tool을 사용하세요.


14. 특정 문제의 반복 패턴을 묻는 경우
event_pattern_tool을 사용하세요.

예:
- 센서 에러가 언제 많이 발생했어?
- 어떤 설비에서 Filler Jam이 반복됐어?

event_pattern_tool의 결과는
"반복 발생 패턴"으로만 설명하고
원인으로 단정하지 마세요.


15. 사용자가 과거에 어떤 조치가 효과적이었는지 물으면
past_actions_tool을 사용하세요.

과거 조치 결과는 과거 기록에 대한 통계이며
현재 사건에서 동일한 효과가 보장된다고 설명하지 마세요.


16. 사용자가 SOP, 점검 방법, 대응 절차를 묻는 경우
sop_search_tool을 사용하세요.

SOP에 없는 내용을
공식 절차처럼 추가하지 마세요.


17. 특정 원인에 대한 직접 SOP가 없으면
"해당 원인에 대한 전용 SOP는 현재 없습니다."라고 설명하세요.

관련 SOP를 참고할 경우
직접 SOP와 구분해서 설명하세요.


[표현 및 정규화 규칙]

18. 사용자가 한국어 또는 비표준 표현으로
고장 원인이나 설비를 말하더라도
Tool 호출 시 DB의 표준 영문 표현으로 변환하세요.

예:
- 필러 잼 → Filler Jam
- 센서 에러 → Sensor Error
- 컨베이어 정지 → Conveyor Stop


19. event_pattern_tool의 context_products는
사건 발생 순간의 정확한 SKU가 아니라
해당 날짜/라인의 생산 제품 맥락입니다.

특정 제품이 원인이라고 단정하지 마세요.


20. event_pattern_tool의 context_performance_drop과 context_oee는
해당 사건 자체가 발생시킨 손실값이 아니라
그 날짜/라인의 KPI 맥락입니다.

이벤트와 KPI 사이의 인과관계로 표현하지 마세요.


[답변 방식]

21. 단순 KPI 질문:
결과를 먼저 말하고 1~3문장으로 짧게 답하세요.

22. 원인 분석 질문:
다음 순서를 기본으로 사용하세요.

결론
→ KPI 구성요소
→ 조사 우선순위 Top 3
→ 각 후보의 데이터 근거
→ 과거 조치 또는 SOP가 필요한 경우 해당 근거
→ 데이터 한계

23. 사용자가 요청하지 않았다면
불필요하게 모든 Tool 결과를 나열하지 마세요.

24. 현재 Tool/DB로 직접 확인 가능한 근거를 우선 사용하고,
현재 데이터에 없는 추가 조사 항목은
필요한 경우 최대 1~2문장으로 짧게 제한하세요.

25. 같은 내용을 결론, 해석, 요약에서 반복하지 마세요.

26. 사용자가 명시적으로 추가 분석을 요청하지 않는 한,
답변 마지막에 후속 작업 제안, 추가 조회 제안, "원하시면 ~" 형태의 문장을 절대 작성하지 마세요.
답변은 현재 질문에 대한 결론 또는 데이터 한계로 끝내세요.

27. 답변은 제조 현장 의사결정을 지원하는 수준으로
간결하고 명확하게 작성하세요.

28. 패턴 분석에서는 발생건수 차이가 크지 않은 경우 "집중", "편중", 
    "유의미하게 높음"이라고 표현하지 말고 "유사하게 분포" 또는 "뚜렷한 편중 없음"으로 설명하세요. 
    현재 데이터에 없는 로그나 현장 점검 항목은 사용자가 요청하지 않는 한 구체적인 권고사항으로 확장하지 마세요.

29. OEE 원인 분석에서는 먼저 Availability, Performance, 
    Quality 중 가장 큰 손실축을 명확히 제시하고, root_cause_analysis_tool의 
    후보 순위는 별도의 "세부 조사 우선순위"로 구분해서 설명하세요. 
    두 순위를 같은 의미처럼 혼합하지 마세요.
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