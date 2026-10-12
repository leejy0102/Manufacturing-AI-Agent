# OpenAI API 연결 테스트
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 프로젝트 루트의 .env 파일 불러오기
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# OpenAI 클라이언트 생성
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 간단한 응답 테스트
response = client.responses.create(
    model="gpt-5-mini",
    input="제조 데이터 분석 AI Agent 연결 테스트입니다. 한 문장으로 답해주세요."
)

print(response.output_text)