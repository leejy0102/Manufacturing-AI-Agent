# PostgreSQL 연결 엔진 생성

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

# 프로젝트 루트의 .env 파일 불러오기
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

# DB 접속 정보
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# PostgreSQL 연결 주소
database_url = (
    f"postgresql+psycopg://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}"
)

# 다른 모듈에서 재사용할 DB 엔진
engine = create_engine(database_url)