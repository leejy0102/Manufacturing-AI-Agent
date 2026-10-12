# 생산계획, 비계획 부동, Performance Loss 데이터를 불러오기
import pandas as pd
import random

production = pd.read_csv("data/production_plan_6months.csv")
downtime = pd.read_csv("data/downtime_events_6months.csv")
performance_loss = pd.read_csv("data/performance_loss_events_6months.csv")

# print(production.head())
# print(downtime.head())
# print(performance_loss.head())

# 날짜 + 라인별 비계획 부동시간 합계 계산
downtime_summary = (
    downtime
    .groupby(["production_date", "line_id"])["duration_minutes"]
    .sum()
    .reset_index()
    .rename(columns={
        "duration_minutes": "downtime_minutes"
    })
)

# print(downtime_summary.head())

# 생산계획 데이터에 날짜 + 라인 기준으로 총 부동시간 붙이기
production = production.merge(
    downtime_summary,
    on=["production_date", "line_id"],
    how="left"
)

# 부동 데이터가 없는 경우 0분으로 처리
production["downtime_minutes"] = (
    production["downtime_minutes"]
    .fillna(0)
    .astype(int)
)

# print(production.head())

# 날짜 + 라인별 Performance Loss 총 지속시간 계산
performance_summary = (
    performance_loss
    .groupby(["production_date", "line_id"])["duration_minutes"]
    .sum()
    .reset_index()
    .rename(columns={
        "duration_minutes": "performance_loss_minutes"
    })
)

# print(performance_summary.head())

# 생산계획 데이터에 날짜 + 라인 기준으로 Performance Loss 시간 붙이기
production = production.merge(
    performance_summary,
    on=["production_date", "line_id"],
    how="left"
)

# Performance Loss가 없는 경우 0분으로 처리
production["performance_loss_minutes"] = (
    production["performance_loss_minutes"]
    .fillna(0)
    .astype(int)
)

# print(production.head())

# 날짜 + 라인별 총 계획시간 계산

production["line_total_planned_minutes"] = (
    production
    .groupby(["production_date", "line_id"])["planned_minutes"]
    .transform("sum")
)

# SKU별 계획시간 비중 계산

production["planned_time_ratio"] = (
    production["planned_minutes"]
    / production["line_total_planned_minutes"]
)

# 라인 전체 부동시간을 SKU별 계획시간 비중으로 배분

production["sku_downtime_minutes"] = (
    production["downtime_minutes"]
    * production["planned_time_ratio"]
).round().astype(int)

# 라인 전체 Performance Loss 시간도 SKU별로 배분

production["sku_performance_loss_minutes"] = (
    production["performance_loss_minutes"]
    * production["planned_time_ratio"]
).round().astype(int)

# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "planned_minutes",
#             "sku_downtime_minutes",
#             "sku_performance_loss_minutes"
#         ]
#     ].head(20)
# )

# SKU별 실제 가동시간 계산
# 계획시간에서 SKU별 비계획 부동시간을 차감
production["run_minutes"] = (
    production["planned_minutes"]
    - production["sku_downtime_minutes"]
)

# 혹시 계산상 음수가 생기지 않도록 0으로 제한
production["run_minutes"] = production["run_minutes"].clip(lower=0)

# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "planned_minutes",
#             "sku_downtime_minutes",
#             "run_minutes"
#         ]
#     ].head(20)
# )


# Availability 계산
# 실제 가동시간 / 계획 생산시간
production["availability"] = (
    production["run_minutes"]
    / production["planned_minutes"]
)

# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "planned_minutes",
#             "run_minutes",
#             "availability"
#         ]
#     ].head(20)
# )


# Performance Loss 이벤트별 속도비율 계산
# 실제속도 / 기준속도
performance_loss["speed_ratio"] = (
    performance_loss["actual_speed"]
    / performance_loss["normal_speed"]
)

# 날짜 + 라인별 Performance Loss 가중 평균 계산
# 이벤트가 길수록 Performance에 더 크게 반영
performance_loss["weighted_speed"] = (
    performance_loss["speed_ratio"]
    * performance_loss["duration_minutes"]
)

performance_ratio_summary = (
    performance_loss
    .groupby(["production_date", "line_id"])
    .agg(
        total_loss_minutes=("duration_minutes", "sum"),
        total_weighted_speed=("weighted_speed", "sum")
    )
    .reset_index()
)

performance_ratio_summary["avg_loss_speed_ratio"] = (
    performance_ratio_summary["total_weighted_speed"]
    / performance_ratio_summary["total_loss_minutes"]
)

# print(performance_ratio_summary.head())

# 날짜 + 라인별 평균 Performance Loss 속도비율을 생산 데이터에 붙이기
production = production.merge(
    performance_ratio_summary[
        [
            "production_date",
            "line_id",
            "avg_loss_speed_ratio"
        ]
    ],
    on=["production_date", "line_id"],
    how="left"
)

# Performance Loss가 없는 경우 정상속도 100%로 처리
production["avg_loss_speed_ratio"] = (
    production["avg_loss_speed_ratio"]
    .fillna(1.0)
)

# SKU별 Performance 계산
# Performance Loss 시간은 저속 운전, 나머지 가동시간은 정상속도라고 가정
production["performance"] = (
    (
        production["run_minutes"]
        - production["sku_performance_loss_minutes"]
    )
    +
    (
        production["sku_performance_loss_minutes"]
        * production["avg_loss_speed_ratio"]
    )
) / production["run_minutes"]

# 계산 안정성을 위해 0~1 범위로 제한
production["performance"] = (
    production["performance"]
    .fillna(0)
    .clip(lower=0, upper=1)
)

# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "run_minutes",
#             "sku_performance_loss_minutes",
#             "avg_loss_speed_ratio",
#             "performance"
#         ]
#     ].head(20)
# )


# 실제 생산량 계산
# 실제 가동시간 × 기준속도 × Performance
production["actual_quantity"] = (
    production["run_minutes"]
    * production["ideal_speed_per_min"]
    * production["performance"]
).round().astype(int)

# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "run_minutes",
#             "ideal_speed_per_min",
#             "performance",
#             "actual_quantity"
#         ]
#     ].head(20)
# )


# Reject율 생성
# 일반 생산일 기준 0.5~2% 범위에서 랜덤 설정
production["reject_rate"] = [
    random.uniform(0.005, 0.02)
    for _ in range(len(production))
]

# Reject 수량 계산
production["reject_quantity"] = (
    production["actual_quantity"]
    * production["reject_rate"]
).round().astype(int)

# 양품 수량 계산
production["good_quantity"] = (
    production["actual_quantity"]
    - production["reject_quantity"]
)

# Quality 계산
# 양품 수량 / 실제 생산량

production["quality"] = (
    production["good_quantity"]
    / production["actual_quantity"]
)

# # 품질 관련 결과 확인
# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "actual_quantity",
#             "reject_quantity",
#             "good_quantity",
#             "quality"
#         ]
#     ].head(20)
# )


# GLY 계산
# 계획 생산량 대비 실제 생산량 비율
production["gly"] = (
    production["actual_quantity"]
    / production["planned_quantity"]
)


# OEE 계산
# Availability × Performance × Quality
production["oee"] = (
    production["availability"]
    * production["performance"]
    * production["quality"]
)

# # 최종 KPI 확인
# print(
#     production[
#         [
#             "production_date",
#             "line_name",
#             "brand_name",
#             "gly",
#             "availability",
#             "performance",
#             "quality",
#             "oee"
#         ]
#     ].head(20)
# )

# # GLY 전체 분포 확인
# print("GLY 최소:", round(production["gly"].min(), 3))
# print("GLY 평균:", round(production["gly"].mean(), 3))
# print("GLY 최대:", round(production["gly"].max(), 3))


# 최종 일별 생산실적 데이터 저장
production.to_csv(
    "data/daily_production_6months.csv",
    index=False
)

print("6개월 일별 생산실적 저장 완료")