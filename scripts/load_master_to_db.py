# PostgreSQL 연결 준비 및 마스터 CSV 불러오기
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

# DB 엔진 생성
engine = create_engine(database_url)

# 마스터 데이터 불러오기
lines = pd.read_csv("data/lines.csv")
equipment = pd.read_csv("data/equipment.csv")
products = pd.read_csv("data/products.csv")

# print(lines.head())
# print(equipment.head())
# print(products.head())


# 마스터 데이터를 PostgreSQL 테이블로 저장
lines.to_sql(
    "lines",
    engine,
    if_exists="replace",
    index=False
)

equipment.to_sql(
    "equipment",
    engine,
    if_exists="replace",
    index=False
)

products.to_sql(
    "products",
    engine,
    if_exists="replace",
    index=False
)

print("마스터 테이블 DB 적재 완료")