import random
import pandas as pd
#랜덤 상품 만들기
products = pd.read_csv("data/products.csv")

can_products = products[products["package_type"] == "CAN"]

num_skus = random.randint(1, 3)

selected_products = can_products.sample(n=num_skus)

print(selected_products)

#랜덤 상품의 생산시간 배분하기(CIP 품종교체 포함)
total_minutes = 480
cip_minutes = 60
changeover_minutes = (num_skus - 1) * 60

available_minutes = total_minutes - cip_minutes - changeover_minutes

min_minutes_per_sku = 60

remaining_minutes = available_minutes - (min_minutes_per_sku * num_skus)

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

print("가용 생산시간:", available_minutes)
print("SKU별 배정시간:", allocated_minutes)

print("가용 생산시간:", available_minutes)
print("SKU별 배정시간:", allocated_minutes)

#계획 생산량 계산로직
ideal_speed = 1000

planned_quantities = [
    minutes * ideal_speed
    for minutes in allocated_minutes
]

print("SKU별 계획 생산량:", planned_quantities)

#표 형태로 묶기
daily_plan = selected_products.copy()

daily_plan["planned_minutes"] = allocated_minutes
daily_plan["planned_quantity"] = planned_quantities

print(daily_plan)

#실제 가동시간을 활용하여 availability 계산
availability_rates = [
    round(random.uniform(0.85, 0.98), 3)
    for _ in range(num_skus)
]

daily_plan["run_minutes"] = (
    daily_plan["planned_minutes"] * availability_rates
).astype(int)

daily_plan["availability"] = (
    daily_plan["run_minutes"] / daily_plan["planned_minutes"]
)

#performance 비율
performance_rates = [
    round(random.uniform(0.85, 0.98), 3)
    for _ in range(num_skus)
]

daily_plan["performance"] = performance_rates

daily_plan["actual_quantity"] = (
    daily_plan["run_minutes"]
    * ideal_speed
    * daily_plan["performance"]
).astype(int)

print(daily_plan)

#리젝트와 양품수량
reject_rates = [
    round(random.uniform(0.005, 0.02), 4)
    for _ in range(num_skus)
]

daily_plan["reject_rate"] = reject_rates

daily_plan["reject_quantity"] = (
    daily_plan["actual_quantity"] * daily_plan["reject_rate"]
).astype(int)

daily_plan["good_quantity"] = (
    daily_plan["actual_quantity"] - daily_plan["reject_quantity"]
)

daily_plan["quality"] = (
    daily_plan["good_quantity"] / daily_plan["actual_quantity"]
)

print(daily_plan)

#GLY OEE 계산
daily_plan["gly"] = (
    daily_plan["actual_quantity"] / daily_plan["planned_quantity"]
)

daily_plan["oee"] = (
    daily_plan["availability"]
    * daily_plan["performance"]
    * daily_plan["quality"]
)

print(daily_plan)