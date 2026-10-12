# 생산계획 데이터를 불러와 계획정지 이벤트 생성을 준비
import pandas as pd

production = pd.read_csv("data/production_plan_6months.csv")

# print(production.head())


# 계획정지 이벤트를 저장할 리스트 생성
planned_downtime_rows = []

# 날짜 + 라인별로 하루 1회 CIP 이벤트 생성
for production_date in production["production_date"].unique():

    daily_data = production[
        production["production_date"] == production_date
    ]

    for line_id in daily_data["line_id"].unique():

        planned_downtime_rows.append({
            "production_date": production_date,
            "line_id": line_id,
            "downtime_type": "CIP",
            "duration_minutes": 60,
            "from_product_id": None,
            "to_product_id": None,
        })

# 생성된 CIP 이벤트 확인
# df_planned_downtime = pd.DataFrame(planned_downtime_rows)

# print(df_planned_downtime.head(20))
# print("총 CIP 이벤트 수:", len(df_planned_downtime))


# 날짜 + 라인별 Changeover 이벤트 생성
# 같은 날 생산 SKU가 2개면 1회, 3개면 2회 발생
for production_date in production["production_date"].unique():

    daily_data = production[
        production["production_date"] == production_date
    ]

    for line_id in daily_data["line_id"].unique():

        line_data = daily_data[
            daily_data["line_id"] == line_id
        ].reset_index(drop=True)

        # 생산 SKU 순서대로 전환 이벤트 생성
        for i in range(len(line_data) - 1):

            from_product_id = line_data.loc[i, "product_id"]
            to_product_id = line_data.loc[i + 1, "product_id"]

            planned_downtime_rows.append({
                "production_date": production_date,
                "line_id": line_id,
                "downtime_type": "CHANGEOVER",
                "duration_minutes": 60,
                "from_product_id": from_product_id,
                "to_product_id": to_product_id,
            })

df_planned_downtime = pd.DataFrame(planned_downtime_rows)

# 생성된 계획정지 이벤트를 DataFrame으로 변환
df_planned_downtime = pd.DataFrame(planned_downtime_rows)

# # 앞부분 데이터 확인
# # print(df_planned_downtime.head(30))

# # CIP / Changeover 건수 확인
# print(df_planned_downtime["downtime_type"].value_counts())

# # 전체 이벤트 수 확인
# print("총 계획정지 이벤트 수:", len(df_planned_downtime))

# # Changeover 이벤트의 전환 제품 확인
# changeover_check = df_planned_downtime[
#     df_planned_downtime["downtime_type"] == "CHANGEOVER"
# ][
#     [
#         "production_date",
#         "line_id",
#         "from_product_id",
#         "to_product_id",
#         "duration_minutes"
#     ]
# ]

# print(changeover_check.head(30))


# 6개월 계획정지 이벤트 CSV 저장
# from_product_id / to_product_id는 제품 마스터의 product_id 기준으로 저장
df_planned_downtime.to_csv(
    "data/planned_downtime_events_6months.csv",
    index=False
)

print("6개월 계획정지 이벤트 저장 완료")