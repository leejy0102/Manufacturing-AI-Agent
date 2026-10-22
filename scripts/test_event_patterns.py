# Downtime 반복 패턴 분석 테스트

from app.analysis.event_patterns import (
    analyze_event_patterns,
)


result = analyze_event_patterns(
    line_name="CAN1",
    downtime_reason="Sensor Error",
    start_date="2026-01-01",
    end_date="2026-06-30",
    top_k=5,
)


print("\n===== 기본 정보 =====")

print(
    "발생건수:",
    result["event_count"]
)

print(
    "총 정지시간:",
    result["total_downtime_minutes"]
)

print(
    "평균 정지시간:",
    result["avg_downtime_minutes"]
)


print("\n===== 설비 패턴 =====")

for row in result["top_equipment"]:
    print(row)


print("\n===== 시간대 패턴 =====")

for row in result["top_hours"]:
    print(row)


print("\n===== 제품 맥락 패턴 =====")

for row in result["top_product_contexts"]:
    print(row)