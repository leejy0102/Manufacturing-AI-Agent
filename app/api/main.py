# # Manufacturing Intelligence Agent API
# # FastAPI 서버가 정상적으로 실행되는지 확인하는 기본 엔드포인트
# from fastapi import FastAPI


# app = FastAPI(
#     title="Manufacturing Intelligence Agent API"
# )


# @app.get("/")
# def root():
#     return {
#         "message": "Manufacturing Intelligence Agent API is running."
#     }



# Streamlit에서 전체 대화 기록을 받아
# LangGraph Agent가 이전 대화 맥락까지 이해하도록 하는 API

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.graph import manufacturing_agent


app = FastAPI(
    title="Manufacturing Intelligence Agent API"
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in request.messages
    ]

    result = manufacturing_agent.invoke(
        {
            "messages": messages
        }
    )

    final_answer = result["messages"][-1].content

    return ChatResponse(
        answer=final_answer
    )