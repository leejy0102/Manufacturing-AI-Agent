# Root Cause Ranking 2차 버전 테스트
# 현재 데이터 + 과거 유사사건 + 과거 조치 이력 확인

from app.analysis.root_cause import rank_root_causes


results = rank_root_causes(
    line_name="CAN1",
    start_date="2026-01-01",
    end_date="2026-01-31",
    top_k=5,
)


for rank, result in enumerate(results, start=1):

    print(f"\n[{rank}위]")

    print("유형:", result["candidate_type"])
    print("원인 후보:", result["cause"])
    print("현재 데이터 점수:", result["base_score"])
    print(
        "유사사건 지원점수:",
        result["similar_event_support"]
    )
    print("최종 점수:", result["score"])

    if result["best_past_action"]:
        action = result["best_past_action"]

        print("과거 최우수 조치:", action["action_type"])
        print("조치 성공률:", action["success_rate_percent"])
        print(
            "평균 효과점수:",
            action["avg_effectiveness_score"]
        )