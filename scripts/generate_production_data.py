import pandas as pd

# 마스터 데이터 불러오기
lines = pd.read_csv("data/lines.csv")
products = pd.read_csv("data/products.csv")

# 6개월 날짜 생성
dates = pd.date_range(
    start="2026-01-01",
    end="2026-06-30",
    freq="D"
)

# 월~금만 남기기
working_dates = dates[dates.weekday < 5]

print("전체 날짜 수:", len(dates))
print("가동일 수:", len(working_dates))
print(lines)

#하루 생산계획 반복문 만들기
import random

production_rows = []

for production_date in working_dates:
    for _, line in lines.iterrows():

        line_id = line["line_id"]
        line_name = line["line_name"]
        line_type = line["line_type"]
        ideal_speed = line["ideal_speed_per_min"]

        # 해당 라인 타입에서 생산 가능한 제품만 선택
        available_products = products[
            products["package_type"] == line_type
        ]

        # 하루 1~3개 SKU 생산
        max_skus = min(3, len(available_products))
        num_skus = random.randint(1, max_skus)

        selected_products = available_products.sample(
            n=num_skus
        )

        print(
            production_date.date(),
            line_name,
            selected_products["brand_name"].tolist()
        )
        # 하루 총 시간
        total_minutes = 480

        # 매일 CIP 60분
        cip_minutes = 60

        # SKU가 2개면 1번, 3개면 2번 품종교체
        changeover_minutes = (num_skus - 1) * 60

        # 실제 생산에 쓸 수 있는 시간
        available_minutes = (
            total_minutes
            - cip_minutes
            - changeover_minutes
        )

        # SKU별 최소 60분 보장
        min_minutes_per_sku = 60

        remaining_minutes = (
            available_minutes
            - min_minutes_per_sku * num_skus
        )

        # 남은 시간을 랜덤 배분
        weights = [random.random() for _ in range(num_skus)]
        weight_sum = sum(weights)

        extra_minutes = [
            round(remaining_minutes * w / weight_sum)
            for w in weights
        ]

        allocated_minutes = [
            min_minutes_per_sku + extra
            for extra in extra_minutes
        ]
        for (_, product), planned_minutes in zip(
            selected_products.iterrows(),
            allocated_minutes
        ):
            planned_quantity = int(planned_minutes * ideal_speed)

            production_rows.append({
                "production_date": production_date.date(),
                "line_id": line_id,
                "line_name": line_name,
                "product_id": product["product_id"],
                "brand_name": product["brand_name"],
                "package_type": product["package_type"],
                "volume_ml": product["volume_ml"],
                "planned_minutes": planned_minutes,
                "planned_quantity": planned_quantity,
                "ideal_speed_per_min": ideal_speed,
            })

        print(
            production_date.date(),
            line_name,
            "SKU:", num_skus,
            "가용시간:", available_minutes,
            "배정시간:", allocated_minutes
        )

df_production = pd.DataFrame(production_rows)

print(df_production.head(20))
print("총 행 수:", len(df_production))

#중간저장
df_production.to_csv(
    "data/production_plan_6months.csv",
    index=False
)

print("6개월 생산계획 저장 완료")

        