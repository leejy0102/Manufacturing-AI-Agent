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
def get_downtime_summary(line_id, start_date, end_date):

    query = text("""
        SELECT
            category,
            reason,
            SUM(duration_minutes) AS total_downtime_minutes,
            COUNT(*) AS event_count,
            ROUND(AVG(duration_minutes)::numeric, 1) AS avg_downtime_minutes
        FROM downtime_events
        WHERE line_id = :line_id
          AND production_date BETWEEN :start_date AND :end_date
        GROUP BY category, reason
        ORDER BY total_downtime_minutes DESC;
    """)

    params = {
        "line_id": line_id,
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


# 4.특정 라인의 기간별 Performance Loss 분석 함수
def get_performance_loss_summary(line_id, start_date, end_date):

    query = text("""
        SELECT
            loss_type,
            SUM(duration_minutes) AS total_loss_minutes,
            COUNT(*) AS event_count,
            ROUND(AVG(duration_minutes)::numeric, 1) AS avg_loss_minutes,
            ROUND(AVG(actual_speed)::numeric, 1) AS avg_actual_speed,
            ROUND(AVG(normal_speed)::numeric, 1) AS avg_normal_speed
        FROM performance_loss_events
        WHERE line_id = :line_id
          AND production_date BETWEEN :start_date AND :end_date
        GROUP BY loss_type
        ORDER BY total_loss_minutes DESC;
    """)

    params = {
        "line_id": line_id,
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


# 6.특정 라인의 기간별 계획정지 분석 함수

def get_planned_downtime_summary(line_id, start_date, end_date):

    query = text("""
        SELECT
            downtime_type,
            COUNT(*) AS event_count,
            SUM(duration_minutes) AS total_planned_downtime_minutes,
            ROUND(AVG(duration_minutes)::numeric, 1) AS avg_duration_minutes
        FROM planned_downtime_events
        WHERE line_id = :line_id
          AND production_date BETWEEN :start_date AND :end_date
        GROUP BY downtime_type
        ORDER BY total_planned_downtime_minutes DESC;
    """)

    params = {
        "line_id": line_id,
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