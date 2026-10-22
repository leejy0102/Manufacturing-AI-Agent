# 제조 분석 Query 함수들을 Tool에서 사용하기 위해 import

from langchain_core.tools import tool

from app.database.queries import (
    get_production_data,
    get_kpi_summary,
    get_downtime_summary,
    get_performance_loss_summary,
    get_quality_summary,
    get_planned_downtime_summary,
    search_sop_documents,
    get_past_actions,
)

from app.analysis.root_cause import rank_root_causes
from app.analysis.event_patterns import analyze_event_patterns

# 1. 제조 데이터 조회 함수를 Agent Tool로 감싸기


@tool
def production_data_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 기간별 생산실적 데이터를 조회한다.

    Args:
        line_name: 생산라인 이름. 예: CAN1, BTL2, PET1
        start_date: 조회 시작일. YYYY-MM-DD 형식
        end_date: 조회 종료일. YYYY-MM-DD 형식

    Returns:
        생산실적 조회 결과
    """

    result = get_production_data(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return result.to_dict(orient="records")


# 2.KPI 조회 함수를 Agent Tool로 감싸기


@tool
def kpi_summary_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 기간별 평균 KPI를 조회한다.

    Args:
        line_name: 생산라인 이름. 예: CAN1, BTL2, PET1
        start_date: 조회 시작일. YYYY-MM-DD 형식
        end_date: 조회 종료일. YYYY-MM-DD 형식

    Returns:
        GLY, Availability, Performance, Quality, OEE 평균값
    """

    result = get_kpi_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return result.to_dict(orient="records")


# # 3.부동시간 분석 함수를 Agent Tool로 감싸기
# from app.database.queries import get_downtime_summary


# @tool
# def downtime_summary_tool(
#     line_id: int,
#     start_date: str,
#     end_date: str
# ):
#     """
#     특정 생산라인의 기간별 비계획 부동 원인을 분석한다.

#     Args:
#         line_id: 생산라인 ID. 예: CAN1은 3
#         start_date: 조회 시작일. YYYY-MM-DD 형식
#         end_date: 조회 종료일. YYYY-MM-DD 형식

#     Returns:
#         부동 대분류, 소분류, 총 부동시간, 발생 건수, 평균 부동시간
#     """

#     result = get_downtime_summary(
#         line_id=line_id,
#         start_date=start_date,
#         end_date=end_date
#     )

#     return result.to_dict(orient="records")


# 3.비계획 정지 요약 Tool
# 사용자는 line_id가 아니라 CAN1, BTL2 같은 line_name만 입력

@tool
def downtime_summary_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 비계획 정지 원인과 시간을 요약합니다.

    Args:
        line_name: 생산라인명 (예: CAN1, BTL2, PET1)
        start_date: 조회 시작일 (YYYY-MM-DD)
        end_date: 조회 종료일 (YYYY-MM-DD)

    Returns:
        정지 원인별 총시간, 발생건수, 평균 정지시간
    """

    df = get_downtime_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return df.to_dict(orient="records")


# # 4.Performance Loss 분석 함수를 Agent Tool로 감싸기

# from app.database.queries import get_performance_loss_summary


# @tool
# def performance_loss_summary_tool(
#     line_id: int,
#     start_date: str,
#     end_date: str
# ):
#     """
#     특정 생산라인의 기간별 Performance Loss 원인을 분석한다.

#     Args:
#         line_id: 생산라인 ID
#         start_date: 조회 시작일. YYYY-MM-DD 형식
#         end_date: 조회 종료일. YYYY-MM-DD 형식

#     Returns:
#         Performance Loss 유형별 총 시간, 발생 건수, 평균 시간,
#         평균 실제속도, 평균 기준속도
#     """

#     result = get_performance_loss_summary(
#         line_id=line_id,
#         start_date=start_date,
#         end_date=end_date
#     )

#     return result.to_dict(orient="records")


# 4.Performance Loss 요약 Tool
# line_name 기준으로 속도 저하 원인 조회

@tool
def performance_loss_summary_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 Performance Loss 원인을 요약합니다.

    Args:
        line_name: 생산라인명 (예: CAN1, BTL2, PET1)
        start_date: 조회 시작일 (YYYY-MM-DD)
        end_date: 조회 종료일 (YYYY-MM-DD)

    Returns:
        속도저하 원인별 총시간, 발생건수, 평균속도
    """

    df = get_performance_loss_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return df.to_dict(orient="records")


# 5. 품질 / Reject 분석 함수를 Agent Tool로 감싸기


@tool
def quality_summary_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 기간별 품질 및 Reject 현황을 분석한다.

    Args:
        line_name: 생산라인 이름. 예: CAN1, BTL2, PET1
        start_date: 조회 시작일. YYYY-MM-DD 형식
        end_date: 조회 종료일. YYYY-MM-DD 형식

    Returns:
        제품별 실제 생산량, Reject 수량, 양품 수량,
        Reject율, 평균 Quality
    """

    result = get_quality_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return result.to_dict(orient="records")


# 6.계획정지 분석 함수를 Agent Tool로 감싸기

# from app.database.queries import get_planned_downtime_summary


# @tool
# def planned_downtime_summary_tool(
#     line_id: int,
#     start_date: str,
#     end_date: str
# ):
#     """
#     특정 생산라인의 기간별 계획정지 현황을 분석한다.

#     Args:
#         line_id: 생산라인 ID. 예: CAN1은 3
#         start_date: 조회 시작일. YYYY-MM-DD 형식
#         end_date: 조회 종료일. YYYY-MM-DD 형식

#     Returns:
#         CIP, Changeover 등 계획정지 유형별 발생 건수,
#         총 계획정지시간, 평균 지속시간
#     """

#     result = get_planned_downtime_summary(
#         line_id=line_id,
#         start_date=start_date,
#         end_date=end_date
#     )

#     return result.to_dict(orient="records")


# 6.계획 정지 요약 Tool
# line_name 기준으로 CIP / Changeover 등 조회

@tool
def planned_downtime_summary_tool(
    line_name: str,
    start_date: str,
    end_date: str
):
    """
    특정 생산라인의 계획 정지를 요약합니다.

    Args:
        line_name: 생산라인명 (예: CAN1, BTL2, PET1)
        start_date: 조회 시작일 (YYYY-MM-DD)
        end_date: 조회 종료일 (YYYY-MM-DD)

    Returns:
        계획 정지 유형별 발생건수와 총시간
    """

    df = get_planned_downtime_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date
    )

    return df.to_dict(orient="records")


# SOP 문서를 벡터 검색해서
# 사용자 질문과 관련된 작업 절차를 반환하는 RAG Tool

@tool
def sop_search_tool(query: str):
    """
    SOP 및 제조 매뉴얼에서 사용자 질문과 관련된
    작업 절차, 원인, 조치 방법을 검색합니다.

    Args:
        query: SOP에서 검색할 자연어 질문

    Returns:
        관련 SOP 문서 Chunk 검색 결과
    """

    results = search_sop_documents(
        query=query,
        top_k=3
    )

    return results


# 과거 조치 이력 조회 Tool
# 특정 Downtime 원인에 대해 과거 조치별 성공률과 효과를 반환

@tool
def past_actions_tool(
    downtime_reason: str,
    top_k: int = 5
):
    """
    특정 Downtime 원인에 대해 과거 조치 이력과
    성공률, 평균 복구시간, 효과점수를 조회합니다.
    """

    return get_past_actions(
        downtime_reason=downtime_reason,
        top_k=top_k
    )


# --------------------------------------------------
# Root Cause Analysis Tool
# 현재 손실 데이터와 과거 유사사건을 기반으로
# 우선 조사해야 할 원인 후보를 순위화한다.
# --------------------------------------------------

@tool
def root_cause_analysis_tool(
    line_name: str,
    start_date: str,
    end_date: str,
    top_k: int = 5,
):
    """
    특정 생산라인과 기간에 대해
    Downtime 및 Performance Loss 데이터를 분석하고,
    과거 유사사건과 과거 조치 이력을 참고하여
    우선 조사해야 할 원인 후보를 순위화합니다.

    이 결과는 실제 근본원인을 확정하는 것이 아니라
    데이터 기반 조사 우선순위를 제공합니다.

    사용 예:
    - CAN1 1월 OEE가 낮은 원인을 분석해줘
    - BTL2의 주요 손실 원인 Top 3 알려줘
    - PET1에서 무엇부터 조사해야 하는지 알려줘
    """

    return rank_root_causes(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date,
        top_k=top_k,
    )


# --------------------------------------------------
# Event Pattern Analysis Tool
# 특정 Downtime Reason이
# 어떤 설비 / 시간대 / 제품 맥락에서 반복되는지 분석한다.
# --------------------------------------------------

@tool
def event_pattern_tool(
    line_name: str,
    downtime_reason: str,
    start_date: str,
    end_date: str,
    top_k: int = 5,
):
    """
    특정 생산라인과 기간에서 특정 Downtime Reason의
    반복 발생 패턴을 분석합니다.

    설비별 발생 빈도,
    시간대별 발생 빈도,
    제품 생산 맥락별 발생 빈도를 제공합니다.

    이 결과는 인과관계를 확정하는 것이 아니라
    반복 발생 패턴을 확인하기 위한 분석 결과입니다.
    """

    return analyze_event_patterns(
        line_name=line_name,
        downtime_reason=downtime_reason,
        start_date=start_date,
        end_date=end_date,
        top_k=top_k,
    )