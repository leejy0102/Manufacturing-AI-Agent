# 생산계획, 라인, 설비 마스터 데이터 불러오기
import pandas as pd
import random
from datetime import datetime, timedelta

production = pd.read_csv("data/production_plan_6months.csv")
lines = pd.read_csv("data/lines.csv")
equipment = pd.read_csv("data/equipment.csv")

print(production.head())
print(lines.head())
print(equipment.head())

# Performance Loss 원인과 발생 비중 정의
performance_loss_types = {
    "Load Congestion": 0.50,
    "Operator Manual Adjustment": 0.30,
    "Minor Repeated Jam": 0.20,
}

# Performance Loss 원인을 설정한 비중에 따라 랜덤 선택
def select_performance_loss_type():
    loss_types = list(performance_loss_types.keys())
    weights = list(performance_loss_types.values())

    selected_loss_type = random.choices(
        loss_types,
        weights=weights,
        k=1
    )[0]

    return selected_loss_type

# # 테스트 출력
# for _ in range(10):
#     print(select_performance_loss_type())


# Performance Loss 이벤트의 지속시간과 실제 속도 저하율 생성
def generate_performance_loss_detail(loss_type):
    if loss_type == "Load Congestion":
        duration_minutes = random.randint(10, 40)
        speed_ratio = random.uniform(0.70, 0.90)

    elif loss_type == "Operator Manual Adjustment":
        duration_minutes = random.randint(10, 30)
        speed_ratio = random.uniform(0.75, 0.90)

    else:  # Minor Repeated Jam
        duration_minutes = random.randint(5, 20)
        speed_ratio = random.uniform(0.65, 0.85)

    return duration_minutes, speed_ratio

# # 테스트 출력
# loss_type = select_performance_loss_type()
# duration, speed_ratio = generate_performance_loss_detail(loss_type)

# print(loss_type)
# print("지속시간:", duration)
# print("속도비율:", round(speed_ratio, 2))


# 하루 라인별 Performance Loss 이벤트 건수 생성
def generate_performance_loss_count():
    return random.randint(1, 4)

# # 테스트 출력
# for _ in range(10):
#     print(generate_performance_loss_count())


# 08:00~16:00 사이에서 Performance Loss 시작시간과 종료시간 생성
def generate_performance_loss_time(production_date, duration_minutes):
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

# # 테스트 출력
# loss_type = select_performance_loss_type()
# duration, speed_ratio = generate_performance_loss_detail(loss_type)

# start_time, end_time = generate_performance_loss_time(
#     "2026-01-05",
#     duration
# )

# print(loss_type)
# print("시작:", start_time)
# print("종료:", end_time)
# print("지속시간:", duration)
# print("속도비율:", round(speed_ratio, 2))


# 6개월 전체 Performance Loss 이벤트를 저장할 리스트
performance_loss_rows = []

# 생산계획 데이터에 있는 날짜와 라인을 기준으로 반복
for production_date in production["production_date"].unique():

    daily_data = production[
        production["production_date"] == production_date
    ]

    for line_id in daily_data["line_id"].unique():

        line_data = daily_data[
            daily_data["line_id"] == line_id
        ]

        # 해당 라인의 기준속도 가져오기
        ideal_speed = line_data.iloc[0]["ideal_speed_per_min"]

        # 하루 라인별 Performance Loss 발생 건수
        loss_count = generate_performance_loss_count()

        # 해당 라인에 속한 설비만 추출
        line_equipment = equipment[
            equipment["line_id"] == line_id
        ]

        for _ in range(loss_count):

            # Performance Loss 원인 선택
            loss_type = select_performance_loss_type()

            # 지속시간과 속도 저하율 생성
            duration_minutes, speed_ratio = generate_performance_loss_detail(
                loss_type
            )

            # 시작시간 / 종료시간 생성
            start_time, end_time = generate_performance_loss_time(
                production_date,
                duration_minutes
            )

            # 해당 라인의 설비 중 하나 선택
            selected_equipment = line_equipment.sample(n=1).iloc[0]

            # 실제 속도 계산
            actual_speed = int(ideal_speed * speed_ratio)

            performance_loss_rows.append({
                "production_date": production_date,
                "line_id": line_id,
                "equipment_id": selected_equipment["equipment_id"],
                "equipment_name": selected_equipment["equipment_name"],
                "loss_type": loss_type,
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
                "normal_speed": ideal_speed,
                "actual_speed": actual_speed,
            })

# 생성된 전체 Performance Loss 이벤트를 DataFrame으로 변환
df_performance_loss = pd.DataFrame(performance_loss_rows)

print(df_performance_loss.head(20))
print("총 Performance Loss 이벤트 수:", len(df_performance_loss))

# 6개월 Performance Loss 이벤트 CSV 저장
df_performance_loss.to_csv(
    "data/performance_loss_events_6months.csv",
    index=False
)

print("6개월 Performance Loss 이벤트 저장 완료")

        