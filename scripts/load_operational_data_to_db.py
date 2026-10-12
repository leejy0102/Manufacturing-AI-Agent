# PostgreSQL 연결 준비 및 운영 데이터 CSV 불러오기
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 프로젝트 루트의 .env 파일 불러오기
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# DB 접속 정보
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# PostgreSQL 연결 주소 생성
database_url = (
    f"postgresql+psycopg://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}"
)

engine = create_engine(database_url)

# 운영 데이터 불러오기
production_plan = pd.read_csv("data/production_plan_6months.csv")
daily_production = pd.read_csv("data/daily_production_6months.csv")
downtime_events = pd.read_csv("data/downtime_events_6months.csv")
performance_loss_events = pd.read_csv(
    "data/performance_loss_events_6months.csv"
)
planned_downtime_events = pd.read_csv(
    "data/planned_downtime_events_6months.csv"
)

# print("production_plan:", len(production_plan))
# print("daily_production:", len(daily_production))
# print("downtime_events:", len(downtime_events))
# print("performance_loss_events:", len(performance_loss_events))
# print("planned_downtime_events:", len(planned_downtime_events))


# 운영 데이터를 PostgreSQL 테이블로 저장
production_plan.to_sql(
    "production_plan",
    engine,
    if_exists="replace",
    index=False
)

daily_production.to_sql(
    "daily_production",
    engine,
    if_exists="replace",
    index=False
)

downtime_events.to_sql(
    "downtime_events",
    engine,
    if_exists="replace",
    index=False
)

performance_loss_events.to_sql(
    "performance_loss_events",
    engine,
    if_exists="replace",
    index=False
)

planned_downtime_events.to_sql(
    "planned_downtime_events",
    engine,
    if_exists="replace",
    index=False
)

print("운영 데이터 DB 적재 완료")