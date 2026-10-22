# 과거 조치 이력 조회 테스트
# 특정 Downtime 원인에서 어떤 조치가 효과적이었는지 확인

from app.database.queries import get_past_actions


results = get_past_actions(
    downtime_reason="Filler Jam",
    top_k=5
)


for index, result in enumerate(results, start=1):

    print(f"\n[{index}]")

    print("조치:", result["action_type"])
    print("사용 횟수:", result["action_count"])
    print("성공 횟수:", result["success_count"])
    print("성공률:", result["success_rate_percent"])
    print("평균 복구시간:", result["avg_recovery_minutes"])
    print(
        "평균 효과점수:",
        result["avg_effectiveness_score"]
    )