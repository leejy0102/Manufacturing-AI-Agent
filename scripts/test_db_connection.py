# .env 파일의 DB 접속정보를 읽어서 PostgreSQL 연결 테스트
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# .env 파일 불러오기
# 프로젝트 루트의 .env 파일을 정확한 경로로 불러오기
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

print("ENV 파일 위치:", env_path)
print("ENV 파일 존재:", env_path.exists())

# DB 접속정보 가져오기
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# .env 값이 정상적으로 읽히는지 확인

print("DB_HOST:", db_host)
print("DB_PORT:", db_port)
print("DB_NAME:", db_name)
print("DB_USER:", db_user)
print("DB_PASSWORD 존재:", db_password is not None)

# PostgreSQL 연결 주소 생성
database_url = (
    f"postgresql+psycopg://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}"
)

# DB 엔진 생성
engine = create_engine(database_url)

# 연결 테스트
with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("DB 연결 성공:", result.scalar())