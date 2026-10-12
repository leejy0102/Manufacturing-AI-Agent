import pandas as pd
import random

#생산계획 데이터와 설비 마스터 불러오기
production = pd.read_csv("data/production_plan_6months.csv")
equipment = pd.read_csv("data/equipment.csv")

print(production.head())
print(equipment.head())

# 부동 원인 대분류별 발생 비중과 소분류 정의
downtime_categories = {
    "EQUIPMENT_FAILURE": {
        "weight": 0.50,
        "reasons": [
            "Filler Jam",
            "Sensor Error",
            "Conveyor Stop",
            "Packer Fault",
            "Line-specific Fault",
        ],
    },

    "QUALITY_ISSUE": {
        "weight": 0.20,
        "reasons": [
            "Fill Defect",
            "Label/Package Defect",
            "Container Damage",
        ],
    },

    "EXTERNAL_FACTOR": {
        "weight": 0.20,
        "reasons": [
            "Utility Issue",
            "Upstream/Downstream Delay",
        ],
    },

    "OPERATION_ISSUE": {
        "weight": 0.05,
        "reasons": [
            "Operator Adjustment",
            "Setup/Cleaning Delay",
        ],
    },

    "MATERIAL_ISSUE": {
        "weight": 0.05,
        "reasons": [
            "Container Shortage",
            "Label/Carton/Cap Shortage",
        ],
    },
}

# 라인별 하루 부동 건수 생성
# 대부분 5~10건, 가끔 11~15건 이상 나오도록 설정

def generate_downtime_count():
    if random.random() < 0.15:
        return random.randint(11, 18)
    else:
        return random.randint(5, 10)
    
# 부동 대분류와 소분류를 랜덤 선택하는 함수

def select_downtime_reason(line_type):
    categories = list(downtime_categories.keys())
    weights = [
        downtime_categories[category]["weight"]
        for category in categories
    ]

    selected_category = random.choices(
        categories,
        weights=weights,
        k=1
    )[0]

    selected_reason = random.choice(
        downtime_categories[selected_category]["reasons"]
    )

    # 라인 타입별 전용 설비 고장으로 변환
    if selected_reason == "Line-specific Fault":
        if line_type == "BOTTLE":
            selected_reason = "Washer Fault"
        elif line_type == "CAN":
            selected_reason = "Depalletizer Fault"
        elif line_type == "PET":
            selected_reason = "Blower Fault"

    return selected_category, selected_reason

# 부동 1건의 지속시간 생성
# 대부분 짧거나 일반적인 부동이며, 대형 부동은 낮은 확률로 발생

def generate_downtime_duration():
    severity = random.random()

    # 약 60%: 간단 이슈
    if severity < 0.60:
        return random.randint(5, 15)

    # 약 35%: 일반 이슈
    elif severity < 0.95:
        return random.randint(16, 60)

    # 약 5%: 대형 이슈
    else:
        return random.randint(61, 240)

# 08:00~16:00 사이에서 부동 시작시간과 종료시간 생성

from datetime import datetime, timedelta

def generate_downtime_time(production_date, duration_minutes):
    shift_start = datetime.combine(
        pd.to_datetime(production_date).date(),
        datetime.strptime("08:00", "%H:%M").time()
    )

    shift_end = datetime.combine(
        pd.to_datetime(production_date).date(),
        datetime.strptime("16:00", "%H:%M").time()
    )

    latest_start = shift_end - timedelta(minutes=duration_minutes)

    random_seconds = random.randint(
        0,
        int((latest_start - shift_start).total_seconds())
    )

    start_time = shift_start + timedelta(seconds=random_seconds)
    end_time = start_time + timedelta(minutes=duration_minutes)

    return start_time, end_time

# 6개월 전체 부동 이벤트를 저장할 리스트

downtime_rows = []

# 생산계획 데이터에 있는 날짜와 라인을 기준으로 반복
for production_date in production["production_date"].unique():

    daily_data = production[
        production["production_date"] == production_date
    ]

    for line_id in daily_data["line_id"].unique():

        line_data = daily_data[
            daily_data["line_id"] == line_id
        ]

        line_type = line_data.iloc[0]["package_type"]

        downtime_count = generate_downtime_count()

        # 해당 날짜/라인의 총 계획 생산시간 계산
        planned_minutes_total = line_data["planned_minutes"].sum()

        # 비계획 부동시간 최대 허용치 설정
        # 일반적으로 계획 생산시간의 15~40% 수준까지만 허용

        # 일반일과 이슈일을 구분해 최대 부동시간 비율 설정
        # 약 12% 확률로 이슈일 발생

        if random.random() < 0.12:
            max_downtime_ratio = random.uniform(0.20, 0.40)
        else:
            max_downtime_ratio = random.uniform(0.05, 0.20)

        remaining_downtime_budget = int(
            planned_minutes_total * max_downtime_ratio
        )

        remaining_downtime_budget = int(
            planned_minutes_total * max_downtime_ratio
        )

        # 해당 라인에 속한 설비만 추출
        line_equipment = equipment[
            equipment["line_id"] == line_id
        ]

        for _ in range(downtime_count):

            # 대분류 / 소분류 선택
            category, reason = select_downtime_reason(line_type)

            # 부동시간 생성
            duration_minutes = generate_downtime_duration()

            # 남은 허용시간보다 크면 잘라냄
            duration_minutes = min(
                duration_minutes,
                remaining_downtime_budget
            )

            # 더 이상 부동을 만들 시간이 없으면 종료
            if duration_minutes <= 0:
                break

            # 시작시간 / 종료시간 생성
            start_time, end_time = generate_downtime_time(
                production_date,
                duration_minutes
            )

            # 해당 라인의 설비 중 하나 랜덤 선택
            selected_equipment = line_equipment.sample(n=1).iloc[0]

            downtime_rows.append({
                "production_date": production_date,
                "line_id": line_id,
                "equipment_id": selected_equipment["equipment_id"],
                "equipment_name": selected_equipment["equipment_name"],
                "category": category,
                "reason": reason,
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
            })
            # 사용한 부동시간만큼 남은 허용시간 차감
            remaining_downtime_budget -= duration_minutes

        # print(
        #     production_date,
        #     "line_id:", line_id,
        #     "부동건수:", downtime_count
        # )

# 생성된 전체 부동 이벤트를 DataFrame으로 변환

df_downtime = pd.DataFrame(downtime_rows)

print(df_downtime.head(20))
print("총 부동 이벤트 수:", len(df_downtime))

# 6개월 부동 이벤트 CSV 저장

df_downtime.to_csv(
    "data/downtime_events_6months.csv",
    index=False
)

print("6개월 부동 이벤트 저장 완료")

# # 날짜 + 라인별 총 부동시간 확인

# downtime_summary = (
#     df_downtime
#     .groupby(["production_date", "line_id"])["duration_minutes"]
#     .sum()
#     .reset_index()
# )

# print(downtime_summary.sort_values(
#     "duration_minutes",
#     ascending=False
# ).head(20))

# # 날짜 + 라인별 평균 부동시간 확인

# print(
#     "평균 부동시간:",
#     round(downtime_summary["duration_minutes"].mean(), 1),
#     "분"
# )