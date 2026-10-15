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
)

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