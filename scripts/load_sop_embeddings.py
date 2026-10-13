# SOP Markdown 문서를 읽어 Chunk로 나누고
# OpenAI Embedding을 생성한 뒤 PostgreSQL pgvector 테이블에 저장
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import text

from app.database.connection import engine


# --------------------------------------------------
# 1. 환경변수 및 경로 설정
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

env_path = PROJECT_ROOT / ".env"
load_dotenv(env_path)

SOP_DIR = PROJECT_ROOT / "docs" / "sop"


# --------------------------------------------------
# 2. Embedding 모델 설정
# text-embedding-3-small의 기본 벡터 차원은 1536
# --------------------------------------------------

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)


# --------------------------------------------------
# 3. SOP 문서를 적당한 크기의 Chunk로 분할
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)


# --------------------------------------------------
# 4. PostgreSQL에 RAG용 테이블 생성
# embedding 컬럼은 pgvector의 vector(1536) 타입 사용
# --------------------------------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sop_documents (
    id SERIAL PRIMARY KEY,
    source_file TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);
"""


with engine.begin() as conn:
    conn.execute(text(CREATE_TABLE_SQL))


# --------------------------------------------------
# 5. 기존 SOP 데이터를 삭제
# 스크립트를 다시 실행해도 중복 저장되지 않도록 초기화
# --------------------------------------------------

with engine.begin() as conn:
    conn.execute(text("DELETE FROM sop_documents;"))


# --------------------------------------------------
# 6. SOP Markdown 파일 읽기
# --------------------------------------------------

documents = []

for file_path in SOP_DIR.glob("*.md"):

    content = file_path.read_text(
        encoding="utf-8"
    )

    chunks = text_splitter.split_text(content)

    for chunk in chunks:
        documents.append(
            {
                "source_file": file_path.name,
                "content": chunk,
            }
        )


print(f"생성된 Chunk 수: {len(documents)}")


# --------------------------------------------------
# 7. 각 Chunk를 Embedding으로 변환 후 DB 저장
# --------------------------------------------------

INSERT_SQL = """
INSERT INTO sop_documents (
    source_file,
    content,
    embedding
)
VALUES (
    :source_file,
    :content,
    CAST(:embedding AS vector)
);
"""


for index, document in enumerate(documents, start=1):

    vector = embeddings.embed_query(
        document["content"]
    )

    # pgvector가 읽을 수 있는 문자열 형태로 변환
    vector_string = "[" + ",".join(
        map(str, vector)
    ) + "]"

    with engine.begin() as conn:
        conn.execute(
            text(INSERT_SQL),
            {
                "source_file": document["source_file"],
                "content": document["content"],
                "embedding": vector_string,
            }
        )

    print(
        f"{index}/{len(documents)} 저장 완료 "
        f"- {document['source_file']}"
    )


print("\nSOP Embedding 저장 완료")