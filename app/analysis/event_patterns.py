# 특정 Downtime Reason이
# 어떤 시간대 / 설비 / 제품 맥락에서 반복되는지 분석하는 모듈
#
# 주의:
# context_products는 해당 사건 발생 시점의 정확한 SKU가 아니라
# 같은 날짜/라인에서 생산된 제품 목록이므로
# "제품 맥락" 수준으로만 해석한다.

from sqlalchemy import text

from app.database.connection import engine


def analyze_event_patterns(
    line_name: str,
    downtime_reason: str,
    start_date: str,
    end_date: str,
    top_k: int = 5,
):

    # --------------------------------------------------
    # 1. 분석 대상 사건 조회
    # --------------------------------------------------

    sql = text("""
        SELECT
            case_id,
            production_date,
            line_name,
            equipment_name,
            downtime_reason,
            start_time,
            downtime_minutes,
            context_products,
            context_performance_drop,
            context_oee

        FROM incident_cases

        WHERE LOWER(line_name) = LOWER(:line_name)

          AND LOWER(downtime_reason)
              = LOWER(:downtime_reason)

          AND production_date
              BETWEEN :start_date AND :end_date

        ORDER BY production_date, start_time
    """)

    with engine.connect() as conn:

        rows = conn.execute(
            sql,
            {
                "line_name": line_name,
                "downtime_reason": downtime_reason,
                "start_date": start_date,
                "end_date": end_date,
            }
        ).mappings().all()


    if not rows:

        return {
            "event_count": 0,
            "message": "조건에 해당하는 사건이 없습니다.",
        }


    # --------------------------------------------------
    # 2. 기본 집계용 변수
    # --------------------------------------------------

    equipment_counts = {}
    hour_counts = {}
    product_context_counts = {}

    total_minutes = 0
    total_performance_drop = 0
    total_oee = 0


    # --------------------------------------------------
    # 3. 사건별 패턴 집계
    # --------------------------------------------------

    for row in rows:

        total_minutes += float(
            row["downtime_minutes"]
        )

        total_performance_drop += float(
            row["context_performance_drop"]
        )

        total_oee += float(
            row["context_oee"]
        )


        # ----------------------------------------------
        # 설비별 발생건수
        # ----------------------------------------------

        equipment = (
            row["equipment_name"]
            if row["equipment_name"]
            else "UNKNOWN"
        )

        equipment_counts[equipment] = (
            equipment_counts.get(
                equipment,
                0
            )
            + 1
        )


        # ----------------------------------------------
        # 시간대별 발생건수
        # ----------------------------------------------

        start_time = row["start_time"]

        if start_time is not None:

            if isinstance(start_time, str):
                # "2026-01-01 12:30:00" 형태 대응
                time_part = start_time.split(" ")[-1]
                hour = int(time_part.split(":")[0])

            else:
                hour = start_time.hour

            hour_counts[hour] = (
                hour_counts.get(
                    hour,
                    0
                )
                + 1
            )


        # ----------------------------------------------
        # 제품 맥락별 발생건수
        # ----------------------------------------------

        context_products = (
            row["context_products"]
            if row["context_products"]
            else "UNKNOWN"
        )

        product_context_counts[
            context_products
        ] = (
            product_context_counts.get(
                context_products,
                0
            )
            + 1
        )


    # --------------------------------------------------
    # 4. 상위 패턴 정렬
    # --------------------------------------------------

    top_equipment = sorted(
        equipment_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]


    top_hours = sorted(
        hour_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]


    top_product_contexts = sorted(
        product_context_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]


    # --------------------------------------------------
    # 5. 최종 결과 반환
    # --------------------------------------------------

    event_count = len(rows)

    return {
        "line_name": line_name,

        "downtime_reason": downtime_reason,

        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },

        "event_count": event_count,

        "total_downtime_minutes": round(
            total_minutes,
            1
        ),

        "avg_downtime_minutes": round(
            total_minutes / event_count,
            1
        ),

        "avg_performance_drop": round(
            total_performance_drop
            / event_count,
            4
        ),

        "avg_context_oee": round(
            total_oee
            / event_count,
            4
        ),

        "top_equipment": [
            {
                "equipment_name": name,
                "event_count": count,
            }
            for name, count
            in top_equipment
        ],

        "top_hours": [
            {
                "hour": hour,
                "event_count": count,
            }
            for hour, count
            in top_hours
        ],

        "top_product_contexts": [
            {
                "context_products": products,
                "event_count": count,
            }
            for products, count
            in top_product_contexts
        ],
    }