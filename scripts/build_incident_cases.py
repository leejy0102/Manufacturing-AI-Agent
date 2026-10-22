# 기존 제조 DB의 Downtime 이벤트를 기준으로
# 같은 날짜/라인의 KPI 및 제품 정보를 결합해
# 유사사건 검색용 incident_cases 테이블을 생성하는 스크립트

import pandas as pd
from sqlalchemy import text

from app.database.connection import engine


# --------------------------------------------------
# 1. Downtime 이벤트 + 라인 + 일별 KPI Context 조회
# --------------------------------------------------

# Downtime 이벤트 1건을 Incident Case 1건으로 유지하면서
# 같은 날짜/라인의 KPI와 생산 SKU 정보를 Context로 결합

QUERY = """
WITH daily_context AS (
    SELECT
        production_date,
        line_id,

        STRING_AGG(
            DISTINCT brand_name,
            ', '
        ) AS context_products,

        AVG(availability) AS context_availability,
        AVG(performance) AS context_performance,
        AVG(quality) AS context_quality,
        AVG(oee) AS context_oee

    FROM daily_production

    GROUP BY
        production_date,
        line_id
)

SELECT
    d.production_date,

    d.line_id,
    l.line_name,

    d.equipment_id,
    d.equipment_name,

    d.category AS downtime_category,
    d.reason AS downtime_reason,

    d.start_time,
    d.end_time,
    d.duration_minutes AS downtime_minutes,

    dc.context_products,
    dc.context_availability,
    dc.context_performance,
    dc.context_quality,
    dc.context_oee

FROM downtime_events d

JOIN lines l
    ON d.line_id = l.line_id

LEFT JOIN daily_context dc
    ON d.production_date = dc.production_date
    AND d.line_id = dc.line_id

ORDER BY
    d.production_date,
    d.line_id,
    d.start_time;
"""


df = pd.read_sql(
    text(QUERY),
    engine
)


# --------------------------------------------------
# 2. Performance Drop 파생 변수 생성
# --------------------------------------------------

df["context_performance_drop"] = (
    1 - df["context_performance"]
)

# 각 Incident Case를 구분하기 위한 고유 Case ID 생성
# 이후 action_history에서 어떤 사건에 대한 조치였는지 연결할 때 사용

df.insert(
    0,
    "case_id",
    range(1, len(df) + 1)
)

# --------------------------------------------------
# 3. 분석용 incident_cases 테이블로 저장
# 원본 테이블은 변경하지 않고 별도 파생 테이블 생성
# --------------------------------------------------

df.to_sql(
    "incident_cases",
    engine,
    if_exists="replace",
    index=False
)


print("incident_cases 테이블 생성 완료")
print(f"총 Case 수: {len(df)}")

print("\nSample:")
print(df.head())

