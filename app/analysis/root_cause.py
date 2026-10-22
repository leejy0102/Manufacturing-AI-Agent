# Downtime과 Performance Loss 데이터를 기반으로
# 현재 손실 수준 + 과거 유사사건 + 과거 조치 이력을 결합하여
# 우선 조사해야 할 원인 후보를 점수화하는 분석 모듈
#
# 주의:
# 이 점수는 "진짜 근본원인 확정"이 아니라,
# 현재 손실 데이터와 과거 유사사건을 바탕으로
# 우선 조사할 원인 후보의 순위를 정하는 용도이다.

from app.database.queries import (
    get_downtime_summary,
    get_performance_loss_summary,
    find_similar_events,
    get_past_actions,
)


def rank_root_causes(
    line_name: str,
    start_date: str,
    end_date: str,
    top_k: int = 5,
):

    candidates = []

    # --------------------------------------------------
    # 1. Downtime 데이터 조회
    # --------------------------------------------------

    downtime_df = get_downtime_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date,
    )

    if not downtime_df.empty:

        total_downtime = downtime_df[
            "total_duration_minutes"
        ].sum()

        total_events = downtime_df[
            "event_count"
        ].sum()

        max_avg_duration = downtime_df[
            "avg_duration_minutes"
        ].max()

        for _, row in downtime_df.iterrows():

            # 전체 Downtime 중 해당 원인이 차지하는 시간 비중
            duration_share = (
                row["total_duration_minutes"]
                / total_downtime
                if total_downtime > 0
                else 0
            )

            # 전체 Downtime Event 중 해당 원인의 발생 빈도 비중
            frequency_share = (
                row["event_count"]
                / total_events
                if total_events > 0
                else 0
            )

            # 평균 정지시간 기준 심각도
            severity_score = (
                row["avg_duration_minutes"]
                / max_avg_duration
                if max_avg_duration > 0
                else 0
            )

            # --------------------------------------------------
            # 현재 기간 데이터 기반 기본 점수
            # --------------------------------------------------

            base_score = (
                duration_share * 0.50
                + frequency_share * 0.30
                + severity_score * 0.20
            )

            # --------------------------------------------------
            # 과거 유사사건 검색
            # --------------------------------------------------

            similar_events = find_similar_events(
                line_name=line_name,
                downtime_reason=row["reason"],
                downtime_minutes=float(
                    row["avg_duration_minutes"]
                ),
                top_k=5,
            )

            if similar_events:

                similar_event_support = sum(
                    event["similarity_score"]
                    for event in similar_events
                ) / len(similar_events)

            else:
                similar_event_support = 0.0

            # --------------------------------------------------
            # 과거 조치 이력 조회
            # 원인 점수에는 직접 반영하지 않고
            # 해당 원인에 대한 대응 근거로만 사용
            # --------------------------------------------------

            past_actions = get_past_actions(
                downtime_reason=row["reason"],
                top_k=3,
            )

            best_past_action = (
                past_actions[0]
                if past_actions
                else None
            )

            # --------------------------------------------------
            # 최종 원인 후보 점수
            # 현재 데이터 80% + 유사사건 지원도 20%
            # --------------------------------------------------

            final_score = (
                base_score * 0.80
                + similar_event_support * 0.20
            )

            # --------------------------------------------------
            # Downtime 후보 저장
            # --------------------------------------------------

            candidates.append(
                {
                    "candidate_type": "DOWNTIME",

                    "cause": row["reason"],

                    "category": row["category"],

                    "base_score": round(
                        float(base_score),
                        4
                    ),

                    "similar_event_support": round(
                        float(similar_event_support),
                        4
                    ),

                    "score": round(
                        float(final_score),
                        4
                    ),

                    "total_minutes": round(
                        float(
                            row["total_duration_minutes"]
                        ),
                        1
                    ),

                    "event_count": int(
                        row["event_count"]
                    ),

                    "avg_duration_minutes": round(
                        float(
                            row["avg_duration_minutes"]
                        ),
                        1
                    ),

                    "best_past_action": best_past_action,

                    "similar_events": similar_events,
                }
            )

    # --------------------------------------------------
    # 2. Performance Loss 데이터 조회
    # --------------------------------------------------

    performance_df = get_performance_loss_summary(
        line_name=line_name,
        start_date=start_date,
        end_date=end_date,
    )

    if not performance_df.empty:

        total_loss_minutes = performance_df[
            "total_loss_minutes"
        ].sum()

        total_events = performance_df[
            "event_count"
        ].sum()

        for _, row in performance_df.iterrows():

            # 전체 Performance Loss 중 시간 비중
            duration_share = (
                row["total_loss_minutes"]
                / total_loss_minutes
                if total_loss_minutes > 0
                else 0
            )

            # 전체 Performance Loss Event 중 발생 빈도 비중
            frequency_share = (
                row["event_count"]
                / total_events
                if total_events > 0
                else 0
            )

            # 기준속도 대비 실제속도 감소율
            speed_loss_ratio = 0

            if row["avg_normal_speed"] > 0:

                speed_loss_ratio = (
                    1
                    - (
                        row["avg_actual_speed"]
                        / row["avg_normal_speed"]
                    )
                )

            # --------------------------------------------------
            # Performance Loss 기본 점수
            # --------------------------------------------------

            base_score = (
                duration_share * 0.50
                + frequency_share * 0.30
                + speed_loss_ratio * 0.20
            )

            # 현재 incident_cases가 Downtime 중심이므로
            # Performance Loss에는 유사사건 점수를 아직 적용하지 않음
            final_score = base_score

            # --------------------------------------------------
            # Performance Loss 후보 저장
            # --------------------------------------------------

            candidates.append(
                {
                    "candidate_type": "PERFORMANCE_LOSS",

                    "cause": row["loss_type"],

                    "category": "PERFORMANCE",

                    "base_score": round(
                        float(base_score),
                        4
                    ),

                    "similar_event_support": None,

                    "score": round(
                        float(final_score),
                        4
                    ),

                    "total_minutes": round(
                        float(
                            row["total_loss_minutes"]
                        ),
                        1
                    ),

                    "event_count": int(
                        row["event_count"]
                    ),

                    "speed_loss_ratio": round(
                        float(speed_loss_ratio),
                        4
                    ),

                    "best_past_action": None,

                    "similar_events": [],
                }
            )

    # --------------------------------------------------
    # 3. 전체 후보를 최종 점수순으로 정렬
    # --------------------------------------------------

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True,
    )

    # --------------------------------------------------
    # 4. 상위 Top K 반환
    # --------------------------------------------------

    return candidates[:top_k]