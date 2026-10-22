# 1.특정 라인의 기간별 생산실적 조회 함수
import pandas as pd
from sqlalchemy import text

from app.database.connection import engine


def get_production_data(line_name, start_date, end_date):

    query = text("""
        SELECT
            production_date,
            line_name,
            brand_name,
            volume_ml,
            planned_quantity,
            actual_quantity,
            good_quantity,
            reject_quantity,
            gly,
            availability,
            performance,
            quality,
            oee
        FROM daily_production
        WHERE line_name = :line_name
          AND production_date BETWEEN :start_date AND :end_date
        ORDER BY production_date;
    """)

    params = {
        "line_name": line_name,
        "start_date": start_date,
        "end_date": end_date,
    }

    with engine.connect() as connection:
        result = pd.read_sql(
            query,
            connection,
            params=params
        )

    return result

# 2.특정 라인의 기간별 평균 KPI 조회 함수
def get_kpi_summary(line_name, start_date, end_date):

    query = text("""
        SELECT
            line_name,
            ROUND(AVG(gly)::numeric, 3) AS avg_gly,
            ROUND(AVG(availability)::numeric, 3) AS avg_availability,
            ROUND(AVG(performance)::numeric, 3) AS avg_performance,
            ROUND(AVG(quality)::numeric, 3) AS avg_quality,
            ROUND(AVG(oee)::numeric, 3) AS avg_oee
        FROM daily_production
        WHERE line_name = :line_name
          AND production_date BETWEEN :start_date AND :end_date
        GROUP BY line_name;
    """)

    params = {
        "line_name": line_name,
        "start_date": start_date,
        "end_date": end_date,
    }

    with engine.connect() as connection:
        result = pd.read_sql(
            query,
            connection,
            params=params
        )

    return result


# 3.특정 라인의 기간별 부동 원인 분석 함수
#  비계획 정지 요약
# 사용자 친화적으로 line_id 대신 line_name을 받아 조회

def get_downtime_summary(line_name, start_date, end_date):

    sql = text("""
        SELECT
            d.category,
            d.reason,
            SUM(d.duration_minutes) AS total_duration_minutes,
            COUNT(*) AS event_count,
            AVG(d.duration_minutes) AS avg_duration_minutes
        FROM downtime_events d
        JOIN lines l
            ON d.line_id = l.line_id
        WHERE l.line_name = :line_name
          AND d.production_date BETWEEN :start_date AND :end_date
        GROUP BY
            d.category,
            d.reason
        ORDER BY
            total_duration_minutes DESC;
    """)

    return pd.read_sql(
        sql,
        engine,
        params={
            "line_name": line_name,
            "start_date": start_date,
            "end_date": end_date
        }
    )


# # 4.특정 라인의 기간별 Performance Loss 분석 함수
# line_id 대신 line_name을 받아 조회

def get_performance_loss_summary(line_name, start_date, end_date):

    sql = text("""
        SELECT
            p.loss_type,
            SUM(p.duration_minutes) AS total_loss_minutes,
            COUNT(*) AS event_count,
            AVG(p.duration_minutes) AS avg_duration_minutes,
            AVG(p.actual_speed) AS avg_actual_speed,
            AVG(p.normal_speed) AS avg_normal_speed
        FROM performance_loss_events p
        JOIN lines l
            ON p.line_id = l.line_id
        WHERE l.line_name = :line_name
          AND p.production_date BETWEEN :start_date AND :end_date
        GROUP BY
            p.loss_type
        ORDER BY
            total_loss_minutes DESC;
    """)

    return pd.read_sql(
        sql,
        engine,
        params={
            "line_name": line_name,
            "start_date": start_date,
            "end_date": end_date
        }
    )


# 5.특정 라인의 기간별 품질/Reject 분석 함수
def get_quality_summary(line_name, start_date, end_date):

    query = text("""
        SELECT
            brand_name,
            SUM(actual_quantity) AS total_actual_quantity,
            SUM(reject_quantity) AS total_reject_quantity,
            SUM(good_quantity) AS total_good_quantity,
            ROUND(
                (
                    SUM(reject_quantity)::numeric
                    / NULLIF(SUM(actual_quantity), 0)
                ) * 100,
                2
            ) AS reject_rate_percent,
            ROUND(AVG(quality)::numeric, 4) AS avg_quality
        FROM daily_production
        WHERE line_name = :line_name
          AND production_date BETWEEN :start_date AND :end_date
        GROUP BY brand_name
        ORDER BY reject_rate_percent DESC;
    """)

    params = {
        "line_name": line_name,
        "start_date": start_date,
        "end_date": end_date,
    }

    with engine.connect() as connection:
        result = pd.read_sql(
            query,
            connection,
            params=params
        )

    return result





# 6. 계획 정지 요약
# line_id 대신 line_name을 받아 조회

def get_planned_downtime_summary(line_name, start_date, end_date):

    sql = text("""
        SELECT
            p.downtime_type,
            COUNT(*) AS event_count,
            SUM(p.duration_minutes) AS total_planned_downtime_minutes,
            AVG(p.duration_minutes) AS avg_duration_minutes
        FROM planned_downtime_events p
        JOIN lines l
            ON p.line_id = l.line_id
        WHERE l.line_name = :line_name
          AND p.production_date BETWEEN :start_date AND :end_date
        GROUP BY
            p.downtime_type
        ORDER BY
            total_planned_downtime_minutes DESC;
    """)

    return pd.read_sql(
        sql,
        engine,
        params={
            "line_name": line_name,
            "start_date": start_date,
            "end_date": end_date
        }
    )



# 사용자 질문을 Embedding으로 변환하고
# pgvector에서 가장 유사한 SOP Chunk를 검색하는 함수

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

from app.database.connection import engine


# 프로젝트 루트의 .env 로드
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


# OpenAI Embedding 모델
sop_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)


def search_sop_documents(query: str, top_k: int = 3):

    # 1. 사용자 질문을 벡터로 변환
    query_vector = sop_embeddings.embed_query(query)

    # pgvector가 읽을 수 있는 문자열 형태로 변환
    vector_string = "[" + ",".join(
        map(str, query_vector)
    ) + "]"

    # 2. 질문 벡터와 가장 가까운 SOP Chunk 검색
    # <=> 는 cosine distance 연산자
    sql = text("""
        SELECT
            id,
            source_file,
            content,
            embedding <=> CAST(:query_vector AS vector) AS distance
        FROM sop_documents
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k;
    """)

    # 3. DB 조회
    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {
                "query_vector": vector_string,
                "top_k": top_k
            }
        )

        rows = result.mappings().all()

    return [dict(row) for row in rows]


# 현재 사건 조건과 과거 Incident Case를 비교하여
# 유사한 사건을 점수화해서 반환
#
# equipment_name과 performance_drop은 선택값으로 두어
# 정보가 없을 때도 유사사건 검색이 가능하도록 구성

def find_similar_events(
    line_name: str,
    downtime_reason: str,
    downtime_minutes: float,
    equipment_name: str | None = None,
    performance_drop: float | None = None,
    top_k: int = 5,
):

    sql = text("""
        SELECT
            case_id,
            production_date,
            line_name,
            equipment_name,
            downtime_category,
            downtime_reason,
            downtime_minutes,
            context_products,
            context_availability,
            context_performance,
            context_performance_drop,
            context_quality,
            context_oee

        FROM incident_cases;
    """)

    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    scored_cases = []


    for row in rows:

        score = 0.0
        total_weight = 0.0


        # ----------------------------------------------
        # 같은 라인
        # ----------------------------------------------

        total_weight += 0.25

        if row["line_name"].lower() == line_name.lower():
            score += 0.25


        # ----------------------------------------------
        # 같은 Downtime Reason
        # ----------------------------------------------

        total_weight += 0.30

        if (
            row["downtime_reason"].lower()
            == downtime_reason.lower()
        ):
            score += 0.30


        # ----------------------------------------------
        # 비슷한 정지시간
        # ----------------------------------------------

        total_weight += 0.20

        duration_difference = abs(
            float(row["downtime_minutes"])
            - downtime_minutes
        )

        duration_similarity = max(
            0,
            1 - (
                duration_difference
                / max(downtime_minutes, 1)
            )
        )

        score += duration_similarity * 0.20


        # ----------------------------------------------
        # 설비 정보가 있을 때만 비교
        # ----------------------------------------------

        if equipment_name is not None:

            total_weight += 0.15

            if (
                row["equipment_name"]
                and row["equipment_name"].lower()
                == equipment_name.lower()
            ):
                score += 0.15


        # ----------------------------------------------
        # Performance Drop 정보가 있을 때만 비교
        # ----------------------------------------------

        if performance_drop is not None:

            total_weight += 0.10

            drop_difference = abs(
                float(row["context_performance_drop"])
                - performance_drop
            )

            drop_similarity = max(
                0,
                1 - (
                    drop_difference
                    / max(performance_drop, 0.01)
                )
            )

            score += drop_similarity * 0.10


        # 사용된 조건들의 가중치 기준으로 0~1 정규화
        normalized_score = (
            score / total_weight
            if total_weight > 0
            else 0
        )


        case = dict(row)

        case["similarity_score"] = round(
            normalized_score,
            4
        )

        scored_cases.append(case)


    # 유사도 높은 순서
    scored_cases.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return scored_cases[:top_k]


# 특정 Downtime 원인에 대해
# 과거 어떤 조치를 했고 성공률과 효과가 어땠는지 요약

def get_past_actions(
    downtime_reason: str,
    top_k: int = 5
):

    sql = text("""
        SELECT
            ah.action_type,

            COUNT(*) AS action_count,

            SUM(
                CASE
                    WHEN ah.success = TRUE THEN 1
                    ELSE 0
                END
            ) AS success_count,

            ROUND(
                (
                    AVG(
                        CASE
                            WHEN ah.success = TRUE THEN 1.0
                            ELSE 0.0
                        END
                    ) * 100
                )::numeric,
                1
            ) AS success_rate_percent,

            ROUND(
                AVG(ah.recovery_minutes)::numeric,
                1
            ) AS avg_recovery_minutes,

            ROUND(
                AVG(ah.effectiveness_score)::numeric,
                3
            ) AS avg_effectiveness_score

        FROM action_history ah

        JOIN incident_cases ic
            ON ah.case_id = ic.case_id

        WHERE LOWER(ic.downtime_reason) = LOWER(:downtime_reason)

        GROUP BY
            ah.action_type

        ORDER BY
            avg_effectiveness_score DESC,
            success_rate_percent DESC

        LIMIT :top_k;
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {
                "downtime_reason": downtime_reason,
                "top_k": top_k
            }
        )

        rows = result.mappings().all()

    return [dict(row) for row in rows]