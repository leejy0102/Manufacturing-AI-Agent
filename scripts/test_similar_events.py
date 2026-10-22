# 유사사건 검색 기능 테스트

from app.database.queries import find_similar_events


results = find_similar_events(
    line_name="CAN1",
    equipment_name="CAN1_Filler",
    downtime_reason="Filler Jam",
    downtime_minutes=30,
    performance_drop=0.08,
    top_k=5,
)


for index, result in enumerate(results, start=1):

    print(f"\n[{index}]")

    print("날짜:", result["production_date"])
    print("라인:", result["line_name"])
    print("설비:", result["equipment_name"])
    print("원인:", result["downtime_reason"])
    print("정지시간:", result["downtime_minutes"])
    print("Performance Drop:", result["context_performance_drop"])
    print("Similarity:", round(result["similarity_score"], 3))