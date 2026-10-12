# 생성된 전체 제조 데이터를 불러와 검증 준비
import pandas as pd

lines = pd.read_csv("data/lines.csv")
equipment = pd.read_csv("data/equipment.csv")
products = pd.read_csv("data/products.csv")

production_plan = pd.read_csv("data/production_plan_6months.csv")
daily_production = pd.read_csv("data/daily_production_6months.csv")
downtime = pd.read_csv("data/downtime_events_6months.csv")
performance_loss = pd.read_csv("data/performance_loss_events_6months.csv")
planned_downtime = pd.read_csv("data/planned_downtime_events_6months.csv")

# print("lines:", len(lines))
# print("equipment:", len(equipment))
# print("products:", len(products))
# print("production_plan:", len(production_plan))
# print("daily_production:", len(daily_production))
# print("downtime:", len(downtime))
# print("performance_loss:", len(performance_loss))
# print("planned_downtime:", len(planned_downtime))


# production_plan과 daily_production의 핵심 키 일치 여부 확인
plan_keys = production_plan[
    ["production_date", "line_id", "product_id"]
].sort_values(
    ["production_date", "line_id", "product_id"]
).reset_index(drop=True)

daily_keys = daily_production[
    ["production_date", "line_id", "product_id"]
].sort_values(
    ["production_date", "line_id", "product_id"]
).reset_index(drop=True)

keys_match = plan_keys.equals(daily_keys)

# print("계획-실적 키 일치:", keys_match)


# 생산수량 관계 검증
# actual_quantity = good_quantity + reject_quantity 인지 확인
quantity_check = (
    daily_production["actual_quantity"]
    ==
    daily_production["good_quantity"]
    + daily_production["reject_quantity"]
)

# print("생산수량 관계 정상:", quantity_check.all())


# KPI 계산식 검증
# GLY = actual_quantity / planned_quantity
# OEE = availability × performance × quality
gly_check = (
    (
        daily_production["actual_quantity"]
        / daily_production["planned_quantity"]
    ).round(6)
    ==
    daily_production["gly"].round(6)
)

oee_check = (
    (
        daily_production["availability"]
        * daily_production["performance"]
        * daily_production["quality"]
    ).round(6)
    ==
    daily_production["oee"].round(6)
)

# print("GLY 계산 정상:", gly_check.all())
# print("OEE 계산 정상:", oee_check.all())


# 시간 관계 검증
# run_minutes는 0 이상이고 planned_minutes를 초과하면 안 됨
run_time_check = (
    (daily_production["run_minutes"] >= 0)
    &
    (daily_production["run_minutes"] <= daily_production["planned_minutes"])
)

# print("가동시간 관계 정상:", run_time_check.all())


# 참조 무결성 검증
# 이벤트/생산 데이터의 line_id, product_id, equipment_id가
# 실제 마스터 데이터에 존재하는지 확인
valid_line_ids = set(lines["line_id"])
valid_product_ids = set(products["product_id"])
valid_equipment_ids = set(equipment["equipment_id"])

line_check = (
    set(daily_production["line_id"]).issubset(valid_line_ids)
    and set(downtime["line_id"]).issubset(valid_line_ids)
    and set(performance_loss["line_id"]).issubset(valid_line_ids)
)

product_check = set(
    daily_production["product_id"]
).issubset(valid_product_ids)

equipment_check = (
    set(downtime["equipment_id"]).issubset(valid_equipment_ids)
    and set(performance_loss["equipment_id"]).issubset(valid_equipment_ids)
)

# print("라인 참조 정상:", line_check)
# print("제품 참조 정상:", product_check)
# print("설비 참조 정상:", equipment_check)


# 부동 대분류 발생 비중 확인 (50 20 20 5 5)
downtime_category_ratio = (
    downtime["category"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)

# print("부동 대분류 비중(%)")
# print(downtime_category_ratio)


# GLY / OEE 평균 및 라인별 평균 확인
print("전체 GLY 평균:", round(daily_production["gly"].mean(), 3))
print("전체 OEE 평균:", round(daily_production["oee"].mean(), 3))

line_kpi_summary = (
    daily_production
    .groupby("line_name")[["gly", "oee"]]
    .mean()
    .round(3)
)

print("\n라인별 평균 KPI")
print(line_kpi_summary)